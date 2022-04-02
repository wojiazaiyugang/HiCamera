"""
获取实时数据
"""
from typer import Typer

from camera import HIKCamera
from camera.data_class import Frame

app = Typer()


@app.command()
def main(ip: str):
    camera = HIKCamera(ip=ip, user_name="admin", password="12345678a")
    camera.start_preview(frame_buffer_size=10)
    while True:
        frame: Frame = camera.get_frame()
        print(f"帧shape{frame.data.shape}，该帧时间为{frame.frame_time}")


if __name__ == '__main__':
    app()
