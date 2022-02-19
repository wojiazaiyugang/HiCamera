"""
录像脚本
"""
import time
from typing import List
from pathlib import Path

import cv2
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
    save_videos = []
    for camera_ip in camera_ips:
        cameras.append(HIKCamera(ip=camera_ip, user_name="admin", password="12345678a"))
    for camera in cameras:
        config = camera.get_compress_config()
        # 视频编码类型：0 - 私有264，1 - 标准h264，2 - 标准mpeg4，7 - M - JPEG，8 - MPEG2，9 - SVAC，10 - 标准h265，0xfe - 自动（和源一致），0xff - 无效
        config.struNormHighRecordPara.byVideoEncType = 10
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
    for camera in cameras:
        camera.start_preview()
    for index, camera in enumerate(cameras):
        save_video = output_dir.joinpath(f"{camera_ips[index]}.mp4")
        save_videos.append(save_video)
        camera.save_real_data(save_video)
    while True:
        try:
            time.sleep(20)
        except KeyboardInterrupt:
            print("停止录像")
            for camera in cameras:
                camera.stop_save_real_data()
                camera.stop_preview()
            print("已经停止")
            break
    print(f"录像结束")
    for save_video in save_videos:
        video = cv2.VideoCapture(str(save_video))
        print(f"{save_video} 帧数{video.get(cv2.CAP_PROP_FRAME_COUNT)}")


if __name__ == '__main__':
    app()
