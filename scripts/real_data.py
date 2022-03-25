"""
获取实时数据
"""
import time

import cv2

from camera import HIKCamera
from camera.data_class import Frame

if __name__ == '__main__':
    camera = HIKCamera(ip="192.168.111.78", user_name="admin", password="12345678a")
    camera.start_preview(frame_buffer_size=10)
    while True:
        frame: Frame = camera.get_frame()
        print(f"帧shape{frame.data.shape}，该帧时间为{frame.frame_time}")
        cv2.putText(frame.data, f"{frame.frame_time}", (300,300),cv2.FONT_HERSHEY_SIMPLEX,2,(0,0,255))
        cv2.imwrite("/workspace/HiBoxing/test.jpg", frame.data)