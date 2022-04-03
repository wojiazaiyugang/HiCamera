import threading
import multiprocessing
import time
from datetime import datetime

import cv2

from camera import HIKCamera
from scripts import get_scripts_output


def record():
    camera = HIKCamera(ip="192.168.111.78", user_name="admin", password="12345678a")
    camera.start_preview()
    video = get_scripts_output(f"{datetime.now():%Y%m%d_%H%M%S.mp4}")
    print(f"开始录像")
    camera.save_real_data(video)
    time.sleep(4)
    camera.stop_save_real_data()
    camera.stop_preview()
    video = cv2.VideoCapture(str(video))
    print(f"录像结束，视频总帧数{video.get(cv2.CAP_PROP_FRAME_COUNT)}")


if __name__ == '__main__':

    while True:

        # record()

        # time.sleep(2)
        # t = multiprocessing.Process(target=record)
        t = threading.Thread(target=record)
        t.start()
        # t.join()
        time.sleep(3)
    # camera.stop_preview()