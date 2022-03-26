"""
获取实时数据
"""
from datetime import datetime
import time

import cv2

from camera import HIKCamera
from camera.data_class import Frame

from pathlib import Path
from infer import VideoWriter

if __name__ == '__main__':
    camera = HIKCamera(ip="192.168.111.78", user_name="admin", password="12345678a")
    camera.start_preview(frame_buffer_size=10)
    video_writer = VideoWriter(Path("/workspace/HiBoxing/test.mp4"))
    for i in range(60 * 25):
        frame: Frame = camera.get_frame()
        print(f"帧shape{frame.data.shape}，该帧时间为{frame.frame_time}，当前时间{datetime.now()}")
        cv2.putText(frame.data, f"{frame.frame_time}", (300, 300), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
        cv2.putText(frame.data, f"{datetime.now()}", (300, 500), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
        video_writer.write(frame.data)
    video_writer.release(compress=True)
