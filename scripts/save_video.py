"""
录像脚本
"""
import time

from camera import HIKCamera
from scripts import get_scripts_output

if __name__ == '__main__':
    camera = HIKCamera(ip="192.168.111.78", user_name="admin", password="12345678a")
    camera.start_preview()
    camera.save_real_data(get_scripts_output("output.mp4"))
    time.sleep(20)
    camera.stop_preview()
