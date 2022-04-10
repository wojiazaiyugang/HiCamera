import os
import shutil
from pathlib import Path

import cv2
import numpy as np


class VideoWriter:
    def __init__(self,
                 output_video: Path):
        self.output_video = output_video
        self.video_writer = None

    def write(self, frame: np.ndarray):
        if not self.video_writer:
            self.video_writer = cv2.VideoWriter(str(self.output_video),
                                                cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), 25,
                                                (int(frame.shape[1]), int(frame.shape[0])))
        self.video_writer.write(frame)

    def release(self, compress: bool = False, bit_rate: float = 2):
        """
        结束写录像，并进行后处理
        :param compress: 是否压缩视频
        :param bit_rate: 压缩视频的码率
        :return:
        """
        if not self.video_writer:
            return
        self.video_writer.release()
        if compress:
            temp_video = Path("temp.mp4")
            os.system(f"ffmpeg -hide_banner """
                      f"""-i {self.output_video} """
                      f"""-c:v h264_nvenc """
                      f"""-b {bit_rate}M """
                      f"""-v error -y """
                      f"""{temp_video}""")
            self.output_video.unlink()
            shutil.move(str(temp_video), str(self.output_video))
