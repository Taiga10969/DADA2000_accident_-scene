import argparse
import os
import re

from moviepy.editor import VideoClip, VideoFileClip
from tqdm import tqdm

parser = argparse.ArgumentParser(description='sup-simcse_training_config')
parser.add_argument('--avi_dir', type=str, default="")
parser.add_argument('--mp4_dir', type=str, default="")
args = parser.parse_args()

os.makedirs(args.mp4_dir, exist_ok=True)

avi_files = sorted(os.listdir(args.avi_dir), key=lambda x: int(re.search(r'\d+', x).group()))[700:]

print("avi_files ; ", avi_files)

for i in tqdm(range(len(avi_files))):
    avi_file_path = os.path.join(args.avi_dir, avi_files[i])
    output_file_path = os.path.join(args.mp4_dir, f"{os.path.splitext(avi_files[i])[0]}.mp4")


    ## convert avi2mp4
    video_clip = VideoFileClip(avi_file_path)
    width = video_clip.size[0]
    height = video_clip.size[1]
    rotation = video_clip.rotation
    fps = video_clip.fps

    # avi動画をMP4に変換して保存
    if rotation == 90:
        video_clip.write_videofile(output_file_path, codec='libx264', ffmpeg_params=["-vf", f"scale={height}:{width}"], verbose=False, logger=None)
    else:
        video_clip.write_videofile(output_file_path, codec='libx264', ffmpeg_params=["-vf", f"scale={width}:{height}"], verbose=False, logger=None)



