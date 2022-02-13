import os
import time
import unittest
import shutil

import cv2
from ping3 import ping

from camera import HIKCamera
from tests import get_test_output, get_test_output_dir


class Test(unittest.TestCase):
    def setUp(self) -> None:
        self.camera_ip = os.environ.get("camera_ip", "192.168.111.78")
        self.camera = HIKCamera(ip=self.camera_ip, user_name="admin", password="12345678a")

    def tearDown(self) -> None:
        shutil.rmtree(get_test_output_dir())

    def test_ping(self):
        """
        测试延迟
        :return:
        """
        # 延迟小于1ms
        self.assertLess(ping(self.camera_ip), 0.001)

    def test_record(self):
        """
        测试录像
        :return:
        """
        output_video = get_test_output("test.mp4")
        self.camera.start_preview()
        self.camera.save_real_data(output_video)
        time.sleep(1)
        self.camera.stop_preview()
        video = cv2.VideoCapture(str(output_video))
        self.assertEqual(int(video.get(cv2.CAP_PROP_FPS)), 25)
        self.assertGreater(video.get(cv2.CAP_PROP_FRAME_COUNT), 20)
        self.assertLess(video.get(cv2.CAP_PROP_FRAME_COUNT), 30)

    def test_get_frame(self):
        self.camera.start_preview(frame_buffer_size=1)
        frame = self.camera.get_frame()
        self.assertIsNotNone(frame, None)

    def test_ccd_config(self):
        config = self.camera.get_ccd_config()
        config.struDayNight.byDayNightFilterType = 0  # 白天
        self.camera.set_ccd_config(config)
        config = self.camera.get_ccd_config()
        self.assertEqual(config.struDayNight.byDayNightFilterType, 0)

    def test_compress_config(self):
        config = self.camera.get_compress_config()
        config.struNormHighRecordPara.byResolution = 64
        self.camera.set_compress_config(config)
        self.assertEqual(config.struNormHighRecordPara.byResolution, 64)
