"""
截图 保存一张图片
"""
import cv2
from typer import Typer

from camera import HIKCamera, Frame

app = Typer()


@app.command()
def main(ip: str, output_image: str):
    """

    :param ip: 相机IP
    :param output_image: 保存图片生成路径
    :return:
    """
    camera = HIKCamera(ip=ip, user_name="admin", password="12345678a")
    camera.start_preview(frame_buffer_size=1)
    frame: Frame = camera.get_frame()
    cv2.imwrite(output_image, frame.data)
    print(f"图片保存至{output_image}")


if __name__ == '__main__':
    app()
