import threading
import multiprocessing
import time
from datetime import datetime

import cv2

from camera import HIKCamera
from scripts import get_scripts_output


def record():
    cameras = []
    videos = []
    for ip in ["192.168.111.77", "192.168.111.75", "192.168.111.78"][2:]:
        camera = HIKCamera(ip=ip, user_name="admin", password="12345678a")
        cameras.append(camera)
        camera.start_preview()
        video = get_scripts_output(f"{datetime.now():%Y%m%d_%H%M%S}_{ip}.mp4")
        camera.save_real_data(video)
        videos.append(video)
    time.sleep(5)
    for camera, video_file in zip(cameras, videos):
        camera.stop_save_real_data()
        camera.stop_preview()
        video = cv2.VideoCapture(str(video_file))
        print(f"录像结束，视频总帧数{video.get(cv2.CAP_PROP_FRAME_COUNT)}")


if __name__ == '__main__':
    while True:
        record()
        # t = threading.Thread(target=record)
        # t.start()
        # time.sleep(8)