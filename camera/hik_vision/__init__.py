import ctypes
import time
from ctypes import cdll, byref, c_char_p, CFUNCTYPE, POINTER, sizeof, pointer, memset, addressof, CDLL
from pathlib import Path
from typing import List, Callable

from camera.hik_vision.type_map import h_LONG, h_DWORD, h_BYTE, h_ULONG, h_CHAR, h_BOOL, h_CHAR_P, h_VOID_P, h_INT, h_UNSIGNED_CHAR_P
from camera.hik_vision.structure import NET_DVR_USER_LOGIN_INFO, NET_DVR_DEVICEINFO_V40, NET_DVR_PREVIEWINFO, NET_DVR_CAMERAPARAMCFG, NET_DVR_VIDEOEFFECT, NET_DVR_GAIN, \
    NET_DVR_WHITEBALANCE, NET_DVR_GAMMACORRECT, NET_DVR_EXPOSURE, NET_DVR_WDR, NET_DVR_DAYNIGHT, NET_DVR_NOISEREMOVE, NET_DVR_CMOSMODECFG, NET_DVR_TIME, NET_DVR_BACKLIGHT, \
    NET_DVR_LOCAL_SDK_PATH, NET_DVR_SYSHEAD, NET_DVR_STREAMDATA, NET_DVR_AUDIOSTREAMDATA, NET_DVR_PRIVATE_DATA

play_lib = cdll.LoadLibrary(str(Path(__file__).parent.joinpath("libs").joinpath("libPlayCtrl.so")))


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

        # self.play_lib = cdll.LoadLibrary(str(Path(__file__).parent.joinpath("libs").joinpath("libPlayCtrl.so")))

        self.user_id = self._login(ip, user_name, password)
        self.preview_handle = None

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

    def start_preview(self):
        """
        开始预览
        :return:
        """
        preview_info = NET_DVR_PREVIEWINFO()
        preview_info.lChannel = 1
        preview_info.dwStreamType = 0
        preview_info.bBlocked = 1
        self.lib.NET_DVR_RealPlay_V40.argtypes = [h_LONG, POINTER(NET_DVR_PREVIEWINFO), h_VOID_P, h_VOID_P]
        self.lib.NET_DVR_RealPlay_V40.restype = h_LONG
        self.preview_handle = self.lib.NET_DVR_RealPlay_V40(self.user_id, byref(preview_info), None, None)
        if self.preview_handle == -1:
            raise Exception(f"预览失败：{self.get_last_error_code()}")

    def stop_preview(self):
        """
        停止预览
        :return:
        """
        self.lib.NET_DVR_StopRealPlay.argtypes = [h_LONG]
        self.lib.NET_DVR_StopRealPlay.restype = h_BOOL
        if not self.lib.NET_DVR_StopRealPlay(self.preview_handle):
            raise Exception(f"停止预览异常：{self.get_last_error_code()}")

    def save_real_data(self, save_file: Path):
        """
        保存录像
        :return:
        """
        if self.preview_handle is None:
            raise Exception(f"没有开启预览，无法保存")
        self.lib.NET_DVR_SaveRealData.argtypes = [h_LONG, POINTER(h_CHAR)]
        self.lib.NET_DVR_SaveRealData.restype = h_BOOL
        if not self.lib.NET_DVR_SaveRealData(self.preview_handle, c_char_p(bytes(str(save_file), self.encoding))):
            raise Exception(f"保存录像异常：{self.get_last_error_code()}")

    def stop_save_real_data(self):
        """
        停止数据捕获
        :return:
        """
        self.lib.NET_DVR_StopSaveRealData.argtypes = [h_LONG]
        self.lib.NET_DVR_StopSaveRealData.restype = h_BOOL
        if not self.lib.NET_DVR_StopSaveRealData(self.preview_handle):
            raise Exception(f"停止数据捕获异常：{self.get_last_error_code()}")

    def set_real_data_callback(self, f: Callable):
        """
        注册实时码流回调数据
        :param f:
        :return:
        """
        if self.preview_handle is None:
            raise Exception()
        real_data_callback = CFUNCTYPE(None, h_LONG, h_DWORD, POINTER(h_BYTE), h_DWORD, h_DWORD)
        cb = real_data_callback(f)
        self.lib.NET_DVR_SetRealDataCallBack.argtypes = [h_LONG, h_VOID_P, h_DWORD]
        self.lib.NET_DVR_SetRealDataCallBack.restype = h_BOOL
        if not self.lib.NET_DVR_SetRealDataCallBack(self.preview_handle, cb, h_DWORD(0)):
            raise Exception(f"注册实时码流回调数据异常：{self.get_last_error_code()}")

    # def set_standard_data_callback(self, f: Callable):
    #     """
    #     注册回调函数，捕获实时码流数据（标准码流）。
    #     """
    #     real_data_callback = CFUNCTYPE(None, h_LONG, h_DWORD, POINTER(h_BYTE), h_DWORD, h_DWORD)
    #     cb = real_data_callback(f)
    #     if not self.call_cpp("NET_DVR_SetStandardDataCallBack", self.preview_handle, cb, None):
    #         raise Exception(f"注册实时标准码流回调数据异常：{self.get_last_error_code()}")

    def get_play_control_port(self) -> int:
        port = h_INT(-1)
        play_lib.PlayM4_GetPort.argtypes = [POINTER(h_INT)]
        play_lib.PlayM4_GetPort.restype = h_INT
        if play_lib.PlayM4_GetPort(byref(port)):
            return port.value
        else:
            raise Exception(f"获取播放通道号失败")

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


from ctypes import memmove, string_at
import cv2
import numpy as np


def dis(nPort, pBuf, nSize, nWidth, nHeight, nStamp, nType, nReserved):
    '''
    显示回调函数
    '''
    bbb = string_at(pBuf, nSize)
    # print(type(bbb))
    nparr = np.frombuffer(bbb, dtype=np.uint8)

    img = nparr.reshape(nHeight * 3//2, nWidth)

    img = cv2.cvtColor(img, cv2.COLOR_YUV2BGR_YV12)
    print(img.shape)
    # print(nPort, type(pBuf), nSize, nWidth, nHeight, nStamp, nType, nReserved)
    # # res = bytearray(nSize)
    # res = (h_BYTE * nSize)()
    # if not memmove(res, pBuf, nWidth * nHeight):
    #     raise RuntimeError("memmove failed")
    # image = np.frombuffer(res, dtype=np.uint8, count=nWidth * nHeight * 3)
    # image = np.reshape(image, (nHeight, nWidth))
    # image = cv2.cvtColor(image, cv2.COLOR_YCrCb2BGR)
    # cv2.imshow("1", image)
    # cv2.waitKey(1)
    # print(image.shape)
    cv2.imwrite("/workspace/HiBoxing/test.jpg", img)


DISPLAYCBFUN = CFUNCTYPE(None, h_LONG, POINTER(h_CHAR), h_LONG, h_LONG, h_LONG, h_LONG, h_LONG, h_LONG)
f = DISPLAYCBFUN(dis)


def standard_real_data_callback(lRealHandle,
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
        print("设置头")
        play_lib.PlayM4_SetStreamOpenMode.argtypes = [h_INT, h_INT]
        play_lib.PlayM4_SetStreamOpenMode.restype = h_INT
        if not play_lib.PlayM4_SetStreamOpenMode(0, 0):
            raise Exception()
        # play_lib.PlayM4_OpenStream.argtypes = [h_INT, POINTER(h_CHAR_P), h_INT, h_INT]
        # play_lib.PlayM4_OpenStream.restype = h_INT
        print(pBuffer, type(pBuffer), dwBufSize)
        if not play_lib.PlayM4_OpenStream(0, pBuffer, dwBufSize, 1024 * 1000):
            raise Exception()
        play_lib.PlayM4_SetDisplayCallBack.argtypes = [h_INT, h_VOID_P]
        play_lib.PlayM4_SetDisplayCallBack.restype = h_INT
        if not play_lib.PlayM4_SetDisplayCallBack(0, f):
            raise Exception()
        if not play_lib.PlayM4_Play(0, None):
            raise Exception()
    elif dwDataType == NET_DVR_STREAMDATA:
        # play_lib.PlayM4_InputData.argtypes = [h_INT, h_UNSIGNED_CHAR_P, h_BYTE]
        # play_lib.PlayM4_InputData.restype = h_INT
        if not play_lib.PlayM4_InputData(0, pBuffer, dwBufSize):
            print(play_lib.PlayM4_GetLastError(0))
            raise Exception()


if __name__ == '__main__':
    camera = HIKCamera(ip="192.168.111.77", user_name="admin", password="12345678a")
    camera.start_preview()
    camera.set_real_data_callback(standard_real_data_callback)
    # camera.get_play_control_port()
    # camera.start_preview()
    # video = Path("/workspace/HiBoxing/test.mp4")
    # camera.save_real_data(video)
    time.sleep(3)

    play_lib.PlayM4_Stop(0)
    play_lib.PlayM4_CloseFile(0)
    play_lib.PlayM4_FreePort(0)
    # camera.stop_preview()
    # camera.get_dvr_config()
    # camera.set_dvr_config()
    # camera.get_dvr_config()
