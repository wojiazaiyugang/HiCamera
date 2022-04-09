"""
录像脚本
"""
import time

import cv2
from typer import Typer

from camera import HIKCamera
from scripts import get_scripts_output

app = Typer()


@app.command()
def record(camera_ip: str):
    """
    录像
    """
    camera = HIKCamera(ip=camera_ip, user_name="admin", password="12345678a")
    camera.start_preview()
    save_video = get_scripts_output(f"{camera_ip}.mp4")
    camera.save_real_data(save_video)
    time.sleep(2)
    camera.stop_save_real_data()
    camera.stop_preview()
    video = cv2.VideoCapture(str(save_video))
    print(f"生成视频{save_video}")
    print(f"FPS(25):{video.get(cv2.CAP_PROP_FPS)}")
    print(f"画面尺寸:w={video.get(cv2.CAP_PROP_FRAME_WIDTH)},h={video.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
    print(f"总帧数(75):{video.get(cv2.CAP_PROP_FRAME_COUNT)}")
    print(f"当前位置(0):{video.get(cv2.CAP_PROP_POS_FRAMES)}")
    print(f"跳至50帧:{video.set(cv2.CAP_PROP_POS_FRAMES, 50)}")
    print(f"当前位置(50):{video.get(cv2.CAP_PROP_POS_FRAMES)}")


if __name__ == '__main__':
    app()
