"""
获取实时数据
"""
import time

from camera import HIKCamera

if __name__ == '__main__':
    camera = HIKCamera(ip="192.168.111.78", user_name="admin", password="12345678a")
    camera.start_preview(frame_buffer_size=10)
    while True:
        frame = camera.get_frame()
        time.sleep(0.05)
        print(frame.shape, f"剩余待读取帧个数{len(camera.frames)}")
