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

annotator = ""

st.sidebar.subheader("config")
annotator = st.sidebar.text_input("Annotator:")

if annotator != "":
    anno_dir = "../dataset/mp4_videos"
    save_dir = f"../annotation/{annotator}/accident_scenes"
    mp4_list = sorted(os.listdir(anno_dir), key=lambda x: int(re.search(r'\d+', x).group()))
    total_cnt = len(mp4_list)
    csv_file_path = os.path.join("../annotation", annotator, "log.csv")
    
    
    scene_type = ["car-to-car", "car-to-bus", "car-to-track", "car-to-pedestrian", "car-to-motorbike", "car-to-bicycle", "property_accident", "ather", "bad_sample"]
    
    os.makedirs(save_dir, exist_ok=True)
    
    # CSVファイルの読み込み、既に評価済みのデータをスキップ
    if os.path.exists(csv_file_path):
        with open(csv_file_path, 'r') as f:
            reader = csv.reader(f)
            existing_files = {row[0] for row in reader if row[0] != 'anno_file'}
    else:
        existing_files = set()
    mp4_list = [file for file in mp4_list if file not in existing_files] # 評価済みを除外
    remaining_cnt = len(mp4_list)
    
    if not mp4_list:
        st.write("すべての画像が評価済みです。")
        st.stop()
    
    anno_file = mp4_list[0]
    video_path = os.path.join(anno_dir, anno_file)
    video_name = os.path.splitext(anno_file)[0]
    
    video_file = open(video_path, 'rb')
    video_bytes = video_file.read()
    
    remaining_percent = (total_cnt-remaining_cnt)/total_cnt*100
    
    # フレーム選択基準の表示
    st.sidebar.subheader("infomation")
    st.sidebar.write(f"**処理中動画：** {video_name}")
    st.sidebar.write(f"**進捗：** {total_cnt-remaining_cnt} / {total_cnt}  ({remaining_percent:.2f} %)")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("フレーム選択基準")
    st.sidebar.write("""
    アノテーションにより選択したフレームでどんな事故であるかの説明を行うことを理想とする。
    そのため事故の瞬間（例: 車と人が接触した瞬間）を選択するのではなく、**その数フレーム前の可能な限りブレ（ぼやけ）が少ないフレームを選択する**こととする。
    これにより、事故の内容（例: 車と車の間からの飛び出し）を1フレームで確認できる。
    """)
    
    st.sidebar.subheader("関連事故の基準")
    st.sidebar.write("""
    - `True`：車載カメラの車が事故に関与
    - `False`：車載カメラの車は事故に無関与
    """)
    
    # 事故タイプの選択基準の表示
    st.sidebar.subheader("事故タイプの選択基準")
    st.sidebar.write("""
    - `car-to-car`：車と車の事故
    - `car-to-bus`：車とバスの事故
    - `car-to-track`：車とトラックの事故
    - `car-to-pedestrian`：車と歩行者との事故
    - `car-to-motorbike`：車とバイクとの事故
    - `car-to-bicycle`：車と自転車との事故
    - `property_accident`：対物事故
    - `ather`：その他
    - `bad_sample`：動画として不成立 / 除外
    """)
    
    st.title("annotating accident scene")
    
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
        q2 = st.selectbox("車載カメラの車が事故に関与していますか? (Is the accident related?)", ["True", "False"], index=0)
    
        if st.button('確定'):
            save_path = os.path.join(save_dir, f"{video_name}.png")
            frame_image.save(save_path)
            st.write(f"フレーム {frame_number} を {save_path} として保存しました。")
    
            ## infomation
            # 解像度 (幅 x 高さ)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            # アスペクト比
            aspect_ratio = width / height
            # フレームレート (fps)
            fps = cap.get(cv2.CAP_PROP_FPS)
            # フレーム数
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) 
            # 動画の長さ (秒)
            duration = frame_count / fps if fps > 0 else 0
    
            # CSVファイルに追加
            new_row = [
                anno_file, 
                video_name, 
                total_frames,
                frame_number, 
                q1, 
                q2,
                aspect_ratio,
                width, 
                height, 
                fps,
                frame_count,
                duration, 
                annotator, 
                datetime.datetime.now(JST),
            ]
            with open(csv_file_path, 'a', newline='') as f:
                writer = csv.writer(f)
                if not os.path.exists(csv_file_path) or os.stat(csv_file_path).st_size == 0:
                    writer.writerow(["anno_file", 
                                     "video_name", 
                                     "total_frames", 
                                     "accident_frames", 
                                     "accident_scene_type", 
                                     "related_to_the_accident",
                                     "aspect_ratio", 
                                     "width", 
                                     "height", 
                                     "fps",
                                     "frame_count",
                                     "duration", 
                                     "annotator", 
                                     "annotation_date"])  # ヘッダー追加
                writer.writerow(new_row)
    
            st.rerun()
    
    else:
        st.write("Unable to load frame.")
    
    # 動画リソースを解放
    cap.release()
    
    st.markdown("---")
    