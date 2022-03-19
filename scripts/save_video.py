"""
录像脚本
"""
import time
from typing import List
from pathlib import Path

import cv2
from typer import Typer

from camera import HIKCamera

app = Typer()


@app.command()
def record(camera_ips: List[str],
           output_dir: Path):
    """
    录像
    """
    output_dir.mkdir(exist_ok=True, parents=True)
    cameras = []
    save_videos = []
    for camera_ip in camera_ips:
        cameras.append(HIKCamera(ip=camera_ip, user_name="admin", password="12345678a"))
    for camera in cameras:
        camera.start_preview()
    for index, camera in enumerate(cameras):
        save_video = output_dir.joinpath(f"{camera_ips[index]}.mp4")
        save_videos.append(save_video)
        camera.save_real_data(save_video)
    while True:
        try:
            time.sleep(20)
        except KeyboardInterrupt:
            print("停止录像")
            for camera in cameras:
                camera.stop_save_real_data()
                camera.stop_preview()
            print("已经停止")
            break
    print(f"录像结束")
    for save_video in save_videos:
        video = cv2.VideoCapture(str(save_video))
        print(f"{save_video} 帧数{video.get(cv2.CAP_PROP_FRAME_COUNT)}")


if __name__ == '__main__':
    app()
