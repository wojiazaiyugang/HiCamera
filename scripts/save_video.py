"""
录像脚本
"""
import time
from pathlib import Path

from camera import HIKCamera

if __name__ == '__main__':
    camera = HIKCamera(ip="192.168.111.78", user_name="admin", password="12345678a")
    camera.start_preview()
    camera.save_real_data(Path("/workspace/HiBoxing/1.mp4"))
    time.sleep(2)
