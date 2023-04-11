import sys
import time
from threading import Thread
from pathlib import Path

import cv2
from typer import Typer

sys.path.append("/home/yujiannan/Projects/HiCamera")
from camera import HIKCamera

app = Typer()


def preview_rtsp_video(user_name: str, password: str, ip: str, port: int = 554):
    cap = cv2.VideoCapture(f"rtsp://{user_name}:{password}@{ip}:{port}/MPEG-4/ch1/main/av_stream")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.namedWindow("1", cv2.WINDOW_KEEPRATIO)
        cv2.imshow("1", frame)
        cv2.waitKey(1)


@app.command()
def preview_and_control(ip: str,
                        user_name: str = "admin",
                        password: str = "12345678a",
                        show: bool = False,
                        control: bool = False):
    """
    相机预览和控制
    :return:
    """
    if show:
        preview_thread = Thread(target=preview_rtsp_video, args=(user_name, password, ip))
        preview_thread.daemon = True
        preview_thread.start()
    hik_camera = HIKCamera(ip=ip,
                           user_name=user_name,
                           password=password)
    if control:
        help_message = (
            f"""特殊命令：reboot:设备重启 save:保存一张图片\n """
            f"""云台命令(输入命令和duration，空格分割，如23 3表示23命令持续3秒)：11:焦距变大(倍率变大) 12:焦距变小(倍率变小) 13:焦点前调 14:焦点后调 15:光圈扩大 16:光圈缩小
            21:云台上仰 22:云台下俯 23:云台左转 24:云台右转"""
        )
        while True:
            print(help_message)
            input_str = input()
            try:
                if input_str == "reboot":
                    hik_camera.reboot()
                elif input_str == "save":
                    output_image = Path(__file__).parent.resolve().joinpath("capture.jpeg")
                    hik_camera.capture_image(output_image)
                    print(f"保存图片{output_image}")
                else:
                    command, duration = input_str.split(" ")
                    hik_camera.ptz_control(int(command), 0, speed=1)
                    time.sleep(float(duration))
                    hik_camera.ptz_control(int(command), 1, speed=1)
            except ValueError as _:
                print("命令格式错误")
    while True:
        time.sleep(5)


if __name__ == '__main__':
    app()
