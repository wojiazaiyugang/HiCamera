import shutil
import time
import unittest

import cv2

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
        # H265
        self.assertEqual(config.struNormHighRecordPara.byVideoEncType, 10)

    def test_record(self):
        """
        测试录像
        :return:
        """
        output_video = get_test_output("test.mp4")
        self.camera.start_preview()
        self.camera.save_real_data(output_video)
        time.sleep(2)
        self.camera.stop_save_real_data()
        self.camera.stop_preview()
        video = cv2.VideoCapture(str(output_video))
        self.assertEqual(int(video.get(cv2.CAP_PROP_FPS)), 25)
        self.assertGreater(video.get(cv2.CAP_PROP_FRAME_COUNT), 48)
        self.assertLess(video.get(cv2.CAP_PROP_FRAME_COUNT), 52)
        self.assertTrue(video.set(cv2.CAP_PROP_POS_FRAMES, 50))

