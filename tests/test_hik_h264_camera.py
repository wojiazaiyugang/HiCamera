import time
import shutil
import unittest

import cv2
from ping3 import ping

from camera import HIKCamera
from tests import get_test_output_dir, get_test_output, get_hik_camera


class Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.camera = get_hik_camera()

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(get_test_output_dir())

    def test_by_video_enc_type(self):
        config = self.camera.get_compress_config()
        # H264
        self.assertEqual(config.struNormHighRecordPara.byVideoEncType, 1)

    def test_get_frame(self):
        self.camera.start_preview(frame_buffer_size=1)
        frame = self.camera.get_frame()
        self.assertIsNotNone(frame, None)
        self.camera.stop_preview()
