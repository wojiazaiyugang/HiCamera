"""
测试SDK和rtsp占用资源情况
"""
import threading

import psutil

import cv2

"""
获取实时数据
"""
import time

from camera import HIKCamera


def sdk(ip):
    camera = HIKCamera(ip=ip, user_name="admin", password="12345678a")
    camera.start_preview(frame_buffer_size=10)
    while True:
        frame = camera.get_frame()
        # print(frame.shape, psutil.cpu_percent())


def rtsp(ip):
    camera = cv2.VideoCapture(f"rtsp://admin:12345678a@{ip}:554/h265/ch1/main/av_stream")
    while True:
        ret, frame = camera.read()
        if not ret:
            break
        # print(frame.shape, psutil.cpu_percent())


if __name__ == '__main__':
    for ip in ["192.168.111.77", "192.168.111.77"]:
        t1 = threading.Thread(target=sdk, args=(ip, ))
        t1.start()
    while True:
        print(psutil.cpu_percent())
        time.sleep(0.05)
