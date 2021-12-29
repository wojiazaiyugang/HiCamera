import time
from ctypes import cdll, byref, c_char_p, CFUNCTYPE, POINTER, string_at
from pathlib import Path

import cv2
import numpy as np

from camera.hik_vision.structure import NET_DVR_USER_LOGIN_INFO, NET_DVR_DEVICEINFO_V40, NET_DVR_PREVIEWINFO, \
    NET_DVR_CAMERAPARAMCFG, NET_DVR_VIDEOEFFECT, NET_DVR_GAIN, \
    NET_DVR_WHITEBALANCE, NET_DVR_GAMMACORRECT, NET_DVR_EXPOSURE, NET_DVR_WDR, NET_DVR_DAYNIGHT, NET_DVR_NOISEREMOVE, \
    NET_DVR_CMOSMODECFG, NET_DVR_TIME, NET_DVR_BACKLIGHT, \
    NET_DVR_LOCAL_SDK_PATH, NET_DVR_SYSHEAD, NET_DVR_STREAMDATA, NET_DVR_AUDIOSTREAMDATA, NET_DVR_PRIVATE_DATA
from camera.hik_vision.type_map import h_LONG, h_DWORD, h_BYTE, h_ULONG, h_CHAR, h_BOOL, h_CHAR_P, h_VOID_P, h_INT, \
    h_UNSIGNED_CHAR_P, h_UINT, h_UNSIGNED_CHAR, h_UBYTE


class HIKCamera:
    """
    海康相机
    """

    def __init__(self, ip: str, user_name: str, password: str):
        """
        相机初始化
        :param ip: 相机IP
        :param user_name: 用户名
        :param password: 密码
        """
        self.encoding = "utf-8"

        self.lib = cdll.LoadLibrary(str(Path(__file__).parent.joinpath("libs").joinpath("libhcnetsdk.so")))
        self.play_lib = cdll.LoadLibrary(str(Path(__file__).parent.joinpath("libs").joinpath("libPlayCtrl.so")))
        # TODO 只能在sdk目录下运行，设置path失败
        # self.lib.NET_DVR_SetSDKInitCfg.argtypes = [h_INT, POINTER(NET_DVR_LOCAL_SDK_PATH)]
        # self.lib.NET_DVR_SetSDKInitCfg.restype = h_BOOL
        # local_sdk_path = NET_DVR_LOCAL_SDK_PATH()
        # local_sdk_path.sPath = bytes(str("./libs"), encoding=self.encoding)
        # if not self.lib.NET_DVR_SetSDKInitCfg(2, byref(local_sdk_path)):
        #     raise Exception(f"初始化失败：{self.get_last_error_code()}")
        self.lib.NET_DVR_Init.argtypes = []
        self.lib.NET_DVR_Init.restype = h_BOOL
        if not self.lib.NET_DVR_Init():
            raise Exception(f"初始化失败：{self.get_last_error_code()}")

        self.user_id = self._login(ip, user_name, password)
        self.preview_handle = None
        self.play_control_port = None  # 播放通道号
        self.frames = []  # frame buffer
        self.frame_buffer_size = None

    def __del__(self):
        self.clean_sdk()

    def clean_sdk(self):
        """
        不再使用时清理相机
        :return:
        """
        self.lib.NET_DVR_Cleanup.argtypes = []
        self.lib.NET_DVR_Cleanup.restype = h_BOOL
        if not self.lib.NET_DVR_Cleanup():
            raise Exception(f"清理SDK失败：{self.get_last_error_code()}")

    def get_last_error_code(self) -> int:
        self.lib.NET_DVR_GetLastError.argtypes = []
        self.lib.NET_DVR_GetLastError.restype = h_DWORD
        return self.lib.NET_DVR_GetLastError()

    def _login(self, ip: str, user_name: str, password: str) -> int:
        """
        相机登录
        :param ip: IP
        :param user_name: 用户名
        :param password: 密码
        :return:
        """
        user_login_info = NET_DVR_USER_LOGIN_INFO()
        user_login_info.wPort = 8000
        user_login_info.sDeviceAddress = bytes(ip, self.encoding)
        user_login_info.sUserName = bytes(user_name, encoding=self.encoding)
        user_login_info.sPassword = bytes(password, encoding=self.encoding)
        device_info = NET_DVR_DEVICEINFO_V40()
        self.lib.NET_DVR_Login_V40.argtypes = [POINTER(NET_DVR_USER_LOGIN_INFO), POINTER(NET_DVR_DEVICEINFO_V40)]
        self.lib.NET_DVR_Login_V40.restype = h_LONG
        user_id = self.lib.NET_DVR_Login_V40(byref(user_login_info), byref(device_info))
        if user_id == -1:
            raise Exception(f"登录异常：{self.get_last_error_code()}")
        else:
            return user_id

    # def get_sdk_version(self) -> str:
    #     """
    #     SDK版本信息，2个高字节表示主版本，2个低字节表示次版本。如0x00030000：表示版本为3.0。
    #     :return:
    #     """
    #     return hex(self.call_cpp("NET_DVR_GetSDKVersion"))

    def start_preview(self, frame_buffer_size: int = 5) -> int:
        """
        开始预览
        :return:
        """
        self.frame_buffer_size = frame_buffer_size
        preview_info = NET_DVR_PREVIEWINFO()
        preview_info.lChannel = 1
        preview_info.dwStreamType = 0
        preview_info.bBlocked = 1
        self.lib.NET_DVR_RealPlay_V40.argtypes = [h_LONG, POINTER(NET_DVR_PREVIEWINFO), h_VOID_P, h_VOID_P]
        self.lib.NET_DVR_RealPlay_V40.restype = h_LONG
        real_data_callback_type = CFUNCTYPE(None, h_LONG, h_DWORD, POINTER(h_UBYTE), h_DWORD, h_VOID_P)
        # noinspection PyAttributeOutsideInit
        # 见standard_real_data_callback中的注释
        self.standard_real_data_callback = real_data_callback_type(self._standard_real_data_callback)
        self.preview_handle = self.lib.NET_DVR_RealPlay_V40(self.user_id, byref(preview_info),
                                                            self.standard_real_data_callback, None)
        if self.preview_handle == -1:
            raise Exception(f"预览失败：{self.get_last_error_code()}")
        return self.preview_handle

    def _get_preview_handle(self) -> int:
        """
        获取预览句柄
        :return:
        """
        if self.preview_handle is not None:
            return self.preview_handle
        return self.start_preview()

    def stop_preview(self):
        """
        停止预览
        :return:
        """
        self.lib.NET_DVR_StopRealPlay.argtypes = [h_LONG]
        self.lib.NET_DVR_StopRealPlay.restype = h_BOOL
        if not self.lib.NET_DVR_StopRealPlay(self._get_preview_handle()):
            raise Exception(f"停止预览异常：{self.get_last_error_code()}")

    def save_real_data(self, save_file: Path):
        """
        保存录像
        :return:
        """
        self.lib.NET_DVR_SaveRealData.argtypes = [h_LONG, POINTER(h_CHAR)]
        self.lib.NET_DVR_SaveRealData.restype = h_BOOL
        if not self.lib.NET_DVR_SaveRealData(self._get_preview_handle(), c_char_p(bytes(str(save_file), self.encoding))):
            self.error("保存录像异常")

    def stop_save_real_data(self):
        """
        停止数据捕获
        :return:
        """
        self.lib.NET_DVR_StopSaveRealData.argtypes = [h_LONG]
        self.lib.NET_DVR_StopSaveRealData.restype = h_BOOL
        if not self.lib.NET_DVR_StopSaveRealData(self._get_preview_handle()):
            self.error("停止数据捕获异常")

    def _get_play_control_port(self) -> int:
        """
        获取播放通道号
        :return:
        """
        if self.play_control_port is not None:
            return self.play_control_port
        port = h_INT(-1)
        self.play_lib.PlayM4_GetPort.argtypes = [POINTER(h_INT)]
        self.play_lib.PlayM4_GetPort.restype = h_INT
        if self.play_lib.PlayM4_GetPort(byref(port)):
            return port.value
        else:
            self.error("获取播放通道号失败")

    # def get_dvr_config(self):
    #     cfg = NET_DVR_CAMERAPARAMCFG()
    #     # cfg.struVideoEffect = NET_DVR_VIDEOEFFECT()
    #     # cfg.struGain = NET_DVR_GAIN()
    #     # cfg.struWhiteBalance = NET_DVR_WHITEBALANCE()
    #     # cfg.struExposure = NET_DVR_EXPOSURE()
    #     # cfg.struGammaCorrect = NET_DVR_GAMMACORRECT()
    #     # cfg.struWdr = NET_DVR_WDR()
    #     # cfg.struDayNight = NET_DVR_DAYNIGHT()
    #     # cfg.struBackLight = NET_DVR_BACKLIGHT()
    #     # cfg.struNoiseRemove = NET_DVR_NOISEREMOVE()
    #     # cfg.struCmosModeCfg = NET_DVR_CMOSMODECFG()
    #     a = h_ULONG(0)
    #     res = self.call_cpp("NET_DVR_GetDVRConfig", self.user_id, 1067, 0xFFFFFFFF, byref(cfg), sizeof(NET_DVR_CAMERAPARAMCFG), byref(a))
    #     print(f"err is {self.get_last_error_code()}")
    #     print(f"函数返回值{res}")
    #     print(cfg.struDayNight.byDayNightFilterType)
    #     return cfg

    # def set_dvr_config(self):
    #     cfg = self.get_dvr_config()
    #     cfg.struDayNight.byDayNightFilterType = 6
    #     res = self.call_cpp("NET_DVR_SetDVRConfig", self.user_id, 1068, 0xFFFFFFFF, byref(cfg), sizeof(NET_DVR_CAMERAPARAMCFG))
    #     print(f"err is {self.get_last_error_code()}")
    #     print(f"函数返回值{res}")
    #     a = 1
    def get_frame(self) -> np.ndarray:
        """
        读一帧图片
        :return:
        """
        while len(self.frames) < 1:
            time.sleep(0.001)
        frame = self.frames[0]
        del self.frames[0]
        return frame

    def _display_callback(self, nPort, pBuf, nSize, nWidth, nHeight, nStamp, nType, nReserved):
        '''
        显示回调函数
        '''
        bytes_data = string_at(pBuf, nSize)
        np_data = np.frombuffer(bytes_data, dtype=np.uint8)
        img = np_data.reshape(nHeight * 3 // 2, nWidth)
        img = cv2.cvtColor(img, cv2.COLOR_YUV2BGR_YV12)
        self.frames.append(img)
        if len(self.frames) > self.frame_buffer_size:
            print("视频画面累积，删除队列前图像")
            del self.frames[0]

    def error(self, reason: str):
        """
        报错
        :param reason:
        :return:
        """
        raise Exception(f"{reason}，错误码：{self.get_last_error_code()}")

    def _standard_real_data_callback(self,
                                     lRealHandle,
                                     dwDataType,
                                     pBuffer,
                                     dwBufSize,
                                     pUser):
        """
        实时数据回调函数
        :param lRealHandle:
        :param dwDataType:
        :param pBuffer:
        :param dwBufSize:
        :return:
        """
        if dwDataType == NET_DVR_SYSHEAD:
            self.play_lib.PlayM4_SetStreamOpenMode.argtypes = [h_INT, h_UINT]
            self.play_lib.PlayM4_SetStreamOpenMode.restype = h_INT
            if not self.play_lib.PlayM4_SetStreamOpenMode(self._get_play_control_port(), 0):
                raise Exception()
            self.play_lib.PlayM4_OpenStream.argtypes = [h_INT, POINTER(h_UNSIGNED_CHAR), h_UINT, h_UINT]
            self.play_lib.PlayM4_OpenStream.restype = h_INT
            if not self.play_lib.PlayM4_OpenStream(0, pBuffer, dwBufSize, 1024 * 1000):
                raise Exception()
            self.play_lib.PlayM4_SetDisplayCallBack.argtypes = [h_INT, h_VOID_P]
            self.play_lib.PlayM4_SetDisplayCallBack.restype = h_INT
            display_callback_type = CFUNCTYPE(None, h_LONG, POINTER(h_CHAR), h_LONG, h_LONG, h_LONG, h_LONG, h_LONG,
                                              h_LONG)
            # noinspection PyAttributeOutsideInit
            # 用于解决ctypes的回调函数中无法访问self的问题，详见
            # https://stackoverflow.com/questions/7259794/how-can-i-get-methods-to-work-as-callbacks-with-python-ctypes/65174074#65174074
            self.display_callback = display_callback_type(self._display_callback)
            if not self.play_lib.PlayM4_SetDisplayCallBack(0, self.display_callback):
                self.error("设置播放回调函数失败")
            if not self.play_lib.PlayM4_Play(0, None):
                self.error("开启播放失败")
        elif dwDataType == NET_DVR_STREAMDATA:
            self.play_lib.PlayM4_InputData.argtypes = [h_INT, POINTER(h_UNSIGNED_CHAR), h_UINT]
            self.play_lib.PlayM4_InputData.restype = h_INT
            if not self.play_lib.PlayM4_InputData(0, pBuffer, dwBufSize):
                self.error("输入视频流错误")


def t1est(ip):
    camera = HIKCamera(ip=ip, user_name="admin", password="12345678a")
    camera.start_preview(frame_buffer_size=1)
    camera.save_real_data(Path(f"/workspace/HiBoxing/{ip}.mp4"))
    time.sleep(3)
    # while True:
    #     time.sleep(0.03)
    #     print(f"{ip}:{len(camera.frames)}")


if __name__ == '__main__':
    import threading, multiprocessing
    t1 = threading.Thread(target=t1est, args=("192.168.111.77",))
    t1.start()
    t2 = threading.Thread(target=t1est, args=("192.168.111.78",))
    t2.start()
    time.sleep(4)
    # camera2 = HIKCamera(ip="192.168.111.78", user_name="admin", password="12345678a")
    # camera2.start_preview(frame_buffer_size=10)

    # camera.set_real_data_callback()
    # camera.get_play_control_port()
    # camera.start_preview()
    # video = Path("/workspace/HiBoxing/test.mp4")
    # camera.save_real_data(video)
    # time.sleep(1)

    # play_lib.PlayM4_Stop(0)
    # play_lib.PlayM4_CloseFile(0)
    # play_lib.PlayM4_FreePort(0)
    # camera.stop_preview()
    # camera.get_dvr_config()
    # camera.set_dvr_config()
    # camera.get_dvr_config()
