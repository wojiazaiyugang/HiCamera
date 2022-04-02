import unittest

from ping3 import ping

from tests import get_hik_camera


class Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.camera = get_hik_camera()

    def test_ping(self):
        """
        测试延迟
        :return:
        """
        # 延迟小于10ms
        self.assertLess(ping(self.camera.ip), 0.01)

    def test_ccd_config(self):
        config = self.camera.get_ccd_config()
        config.struDayNight.byDayNightFilterType = 0  # 白天
        self.camera.set_ccd_config(config)
        config = self.camera.get_ccd_config()
        self.assertEqual(config.struDayNight.byDayNightFilterType, 0)

    def test_compress_config(self):
        config = self.camera.get_compress_config()
        config.struNormHighRecordPara.byBitrateType = 1  # 定码率
        self.camera.set_compress_config(config)
        self.assertEqual(config.struNormHighRecordPara.byBitrateType, 1)
