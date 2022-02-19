"""
录像脚本
"""
import time
from typing import List
from pathlib import Path

from typer import Typer

from camera import HIKCamera

app = Typer()


@app.command()
def record(camera_ips: List[str],
           output_dir: Path):
    """
    录像
    """
    cameras = []
    for camera_ip in camera_ips:
        cameras.append(HIKCamera(ip=camera_ip, user_name="admin", password="12345678a"))
    for camera in cameras:
        config = camera.get_compress_config()
        # 中场视角2k，8m
        # 视频分辨率 70-2k
        config.struNormHighRecordPara.byResolution = 70
        # 视频码率 26-8192K
        config.struNormHighRecordPara.dwVideoBitrate = 26
        # 码流类型 0-视频流，1-复合流
        config.struNormHighRecordPara.byStreamType = 0
        # 码率类型 0-变码率，1-定码率
        config.struNormHighRecordPara.byBitrateType = 1
        camera.set_compress_config(config)
    for index, camera in enumerate(cameras):
        camera.start_preview()
        camera.save_real_data(output_dir.joinpath(f"{camera_ips[index]}.mp4"))
    while True:
        try:
            time.sleep(20)
        except KeyboardInterrupt:
            print("停止录像")
            for camera in cameras:
                camera.stop_save_real_data()
                camera.stop_preview()
            print("已经停止")


if __name__ == '__main__':
    app()
