import os
import re
import csv
import streamlit as st
import cv2
from PIL import Image
import datetime

st.set_page_config(
    page_title="annotating accident scene",
    page_icon="✏️",
    #layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)

t_delta = datetime.timedelta(hours=9)
JST = datetime.timezone(t_delta, 'JST')

anno_dir = "../dataset/mp4_videos"
save_dir = "../annotation/accident_scenes"
mp4_list = sorted(os.listdir(anno_dir), key=lambda x: int(re.search(r'\d+', x).group()))
csv_file_path = os.path.join("../annotation", "log.csv")


scene_type = ["car-to-car", "car-to-pedestrian", "car-to-motorbike", "car-to-bicycle", "property_damage", "ather", "bad_sample"]

os.makedirs(save_dir, exist_ok=True)

# CSVファイルの読み込み、既に評価済みのデータをスキップ
if os.path.exists(csv_file_path):
    with open(csv_file_path, 'r') as f:
        reader = csv.reader(f)
        existing_files = {row[0] for row in reader if row[0] != 'anno_file'}
else:
    existing_files = set()
mp4_list = [file for file in mp4_list if file not in existing_files] # 評価済みを除外


print("mp4_list : ", mp4_list)

if not mp4_list:
    st.write("すべての画像が評価済みです。")
    st.stop()


st.title("annotating accident scene")

anno_file = mp4_list[0]
video_path = os.path.join(anno_dir, anno_file)
video_name = os.path.splitext(anno_file)[0]

video_file = open(video_path, 'rb')
video_bytes = video_file.read()

st.write(f"📼**video** : 全体の動画を確認 ({video_name})")
st.video(video_bytes)



st.write("✏️**annotation**")
st.text("事故の瞬間のフレームを選択")
cap = cv2.VideoCapture(video_path)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
frame_number = st.slider('フレームをスクロースして選択 / 事故の内容のアノテーション を行い[確定]．', 0, total_frames - 1, 0)


cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
ret, frame = cap.read()

if ret:
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    frame_image = Image.fromarray(frame)
    st.image(frame_image, caption=f"Frame {frame_number}", use_column_width=True)

    q1 = st.selectbox("accident scene type", scene_type, index=0)

    if st.button('確定'):
        save_path = os.path.join(save_dir, f"{video_name}.png")
        frame_image.save(save_path)
        st.write(f"フレーム {frame_number} を {save_path} として保存しました。")

        # CSVファイルに追加

        new_row = [
            anno_file, 
            video_name, 
            total_frames,
            frame_number, 
            q1, 
            datetime.datetime.now(JST),
        ]
        with open(csv_file_path, 'a', newline='') as f:
            writer = csv.writer(f)
            if not os.path.exists(csv_file_path) or os.stat(csv_file_path).st_size == 0:
                writer.writerow(["anno_file", "video_name", "total_frames", "accident_frames", "accident scene type", "annotation_date"])  # ヘッダー追加
            writer.writerow(new_row)

        st.rerun()

else:
    st.write("Unable to load frame.")

# 動画リソースを解放
cap.release()
