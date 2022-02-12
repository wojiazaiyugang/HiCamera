import os
import time
from ctypes import cdll, byref, c_char_p, CFUNCTYPE, POINTER, string_at, sizeof, c_long
from pathlib import Path

import cv2
import numpy as np

from camera.hik_vision.structure import NET_DVR_USER_LOGIN_INFO, NET_DVR_DEVICEINFO_V40, NET_DVR_PREVIEWINFO, \
    NET_DVR_CAMERAPARAMCFG, NET_DVR_VIDEOEFFECT, NET_DVR_GAIN, \
    NET_DVR_WHITEBALANCE, NET_DVR_GAMMACORRECT, NET_DVR_EXPOSURE, NET_DVR_WDR, NET_DVR_DAYNIGHT, NET_DVR_NOISEREMOVE, \
    NET_DVR_CMOSMODECFG, NET_DVR_TIME, NET_DVR_BACKLIGHT, \
    NET_DVR_LOCAL_SDK_PATH, NET_DVR_SYSHEAD, NET_DVR_STREAMDATA, NET_DVR_AUDIOSTREAMDATA, NET_DVR_PRIVATE_DATA
from camera.hik_vision.type_map import LONG, DWORD, BYTE, BOOL, LPVOID, UBYTE, CHAR, INT, UINT, UNSIGNED_CHAR, CHAR_P


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
        libs_dir = Path(__file__).parent.joinpath("libs")
        os.chdir(libs_dir)
        self.lib = cdll.LoadLibrary(str(libs_dir.joinpath("libhcnetsdk.so")))
        self.lib.NET_DVR_Init.argtypes = []
        self.lib.NET_DVR_Init.restype = BOOL
        if not self.lib.NET_DVR_Init():
            raise Exception(f"初始化失败：{self.get_last_error_code()}")
        self.play_lib = cdll.LoadLibrary(str(libs_dir.joinpath("libPlayCtrl.so")))
        self.user_id = self._login(ip, user_name, password)
        self.preview_handle = None
        self.play_control_port = None  # 播放通道号
        self.frames = []  # frame buffer
        self.frame_buffer_size = None

    def __del__(self):
        self.clean_sdk()

    # def stop_play(self):
    #     """
    #     停止播放
    #     """
    #     if self.play_control_port is None:
    #         return
    #     port = self._get_play_control_port()
    #     self.play_control_port = None
    #     self.play_lib.PlayM4_Stop.argtypes = [h_INT]
    #     self.play_lib.PlayM4_Stop.restype = h_INT
    #     if not self.play_lib.PlayM4_Stop(port):
    #         self.error(f"停止播放错误")
    #     # self.play_lib.PlayM4_CloseFile.argtypes = [h_INT]
    #     # self.play_lib.PlayM4_CloseFile.restype = h_INT
    #     # if not self.play_lib.PlayM4_CloseFile(self._get_play_control_port()):
    #     #     self.error(f"关闭文件错误")
    #     self.play_lib.PlayM4_FreePort.argtypes = [h_INT]
    #     self.play_lib.PlayM4_FreePort.restype = h_INT
    #     if not self.play_lib.PlayM4_FreePort(port):
    #         self.error(f"释放播放通道号错误")

    def _logout(self):
        self.lib.NET_DVR_Logout.argtypes = [LONG]
        self.lib.NET_DVR_Logout.restype = BOOL
        if not self.lib.NET_DVR_Logout(self._get_preview_handle()):
            self.error(f"登出错误")

    def clean_sdk(self):
        """
        不再使用时清理相机
        :return:
        """
        self.lib.NET_DVR_Cleanup.argtypes = []
        self.lib.NET_DVR_Cleanup.restype = BOOL
        if not self.lib.NET_DVR_Cleanup():
            raise Exception(f"清理SDK失败：{self.get_last_error_code()}")

    def get_last_error_code(self) -> int:
        self.lib.NET_DVR_GetLastError.argtypes = []
        self.lib.NET_DVR_GetLastError.restype = DWORD
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
        user_login_info.sDeviceAddress = bytes(ip, encoding=self.encoding)
        user_login_info.sUserName = bytes(user_name, encoding=self.encoding)
        user_login_info.sPassword = bytes(password, encoding=self.encoding)
        device_info = NET_DVR_DEVICEINFO_V40()
        self.lib.NET_DVR_Login_V40.argtypes = [POINTER(NET_DVR_USER_LOGIN_INFO), POINTER(NET_DVR_DEVICEINFO_V40)]
        self.lib.NET_DVR_Login_V40.restype = LONG
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

    def start_preview(self, frame_buffer_size: int = None) -> int:
        """
        开始预览
        :return:
        """
        self.frame_buffer_size = frame_buffer_size
        preview_info = NET_DVR_PREVIEWINFO()
        preview_info.lChannel = 1
        preview_info.dwStreamType = 0
        preview_info.bBlocked = 1
        self.lib.NET_DVR_RealPlay_V40.argtypes = [LONG, POINTER(NET_DVR_PREVIEWINFO), LPVOID, LPVOID]
        self.lib.NET_DVR_RealPlay_V40.restype = LONG
        real_data_callback_type = CFUNCTYPE(None, LONG, DWORD, POINTER(BYTE), DWORD, LPVOID)
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
        self.lib.NET_DVR_StopRealPlay.argtypes = [LONG]
        self.lib.NET_DVR_StopRealPlay.restype = BOOL
        if not self.lib.NET_DVR_StopRealPlay(self._get_preview_handle()):
            raise Exception(f"停止预览异常：{self.get_last_error_code()}")

    def save_real_data(self, save_file: Path, stream_type: int = 1):
        """
        保存录像
        :param save_file: 保存文件路径
        :param stream_type: 保存流类型
        1: mp4v
        2: avc1
        :return:
        """
        self.lib.NET_DVR_SaveRealData_V30.argtypes = [LONG, DWORD, POINTER(CHAR)]
        self.lib.NET_DVR_SaveRealData_V30.restype = BOOL
        if not self.lib.NET_DVR_SaveRealData_V30(self._get_preview_handle(), stream_type,
                                                 c_char_p(bytes(str(save_file), self.encoding))):
            self.error("保存录像异常")

    def stop_save_real_data(self):
        """
        停止数据捕获
        :return:
        """
        self.lib.NET_DVR_StopSaveRealData.argtypes = [LONG]
        self.lib.NET_DVR_StopSaveRealData.restype = BOOL
        if not self.lib.NET_DVR_StopSaveRealData(self._get_preview_handle()):
            self.error("停止数据捕获异常")

    def _get_play_control_port(self) -> int:
        """
        获取播放通道号
        :return:
        """
        if self.play_control_port is not None:
            return self.play_control_port
        port = INT(-1)
        self.play_lib.PlayM4_GetPort.argtypes = [POINTER(INT)]
        self.play_lib.PlayM4_GetPort.restype = INT
        if self.play_lib.PlayM4_GetPort(byref(port)):
            self.play_control_port = port.value
            return self.play_control_port
        else:
            self.error("获取播放通道号失败")

    def get_dvr_config(self) -> NET_DVR_CAMERAPARAMCFG:
        """
        获取设备的配置信息
        :return:
        """
        cfg = NET_DVR_CAMERAPARAMCFG()
        self.lib.NET_DVR_GetDVRConfig.argtypes = [LONG, DWORD, LONG, LPVOID, DWORD, POINTER(DWORD)]
        self.lib.NET_DVR_GetDVRConfig.restype = BOOL
        if not self.lib.NET_DVR_GetDVRConfig(self.user_id, 1067, 0xFFFFFFFF, byref(cfg), sizeof(cfg), byref(DWORD(0))):
            self.error("获取设备配置失败")
        return cfg

    def set_dvr_config(self, cfg: NET_DVR_CAMERAPARAMCFG):
        """
        设置参数
        :param cfg:
        :return:
        """
        self.lib.NET_DVR_SetDVRConfig.argtypes = [LONG, DWORD, LONG, POINTER(NET_DVR_CAMERAPARAMCFG), DWORD]
        self.lib.NET_DVR_SetDVRConfig.restype = BOOL
        if not self.lib.NET_DVR_SetDVRConfig(self.user_id, 1068, 0xFFFFFFFF, byref(cfg), sizeof(cfg)):
            self.error("设置前端参数失败")

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
        if self.frame_buffer_size is None:
            return
        bytes_data = string_at(pBuf, nSize)
        np_data = np.frombuffer(bytes_data, dtype=np.uint8)
        img = np_data.reshape(nHeight * 3 // 2, nWidth)
        img = cv2.cvtColor(img, cv2.COLOR_YUV2BGR_YV12)
        self.frames.append(img)
        if len(self.frames) > self.frame_buffer_size:
            del self.frames[0]

    def error(self, reason: str):
        """
        报错
        :param reason:
        :return:
        """
        error_code = self.get_last_error_code()
        if error_code != 0:
            raise Exception(f"{reason}，错误码：{error_code}")

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
            self.play_lib.PlayM4_SetStreamOpenMode.argtypes = [INT, UINT]
            self.play_lib.PlayM4_SetStreamOpenMode.restype = INT
            # 重复设置可能会出错，忽略即可
            self.play_lib.PlayM4_SetStreamOpenMode(self._get_play_control_port(), 0)
            self.play_lib.PlayM4_OpenStream.argtypes = [INT, POINTER(UNSIGNED_CHAR), UINT, UINT]
            self.play_lib.PlayM4_OpenStream.restype = INT
            if not self.play_lib.PlayM4_OpenStream(self._get_play_control_port(), pBuffer, dwBufSize, 1024 * 1000):
                self.error("开启播放流错误")
            self.play_lib.PlayM4_SetDisplayCallBack.argtypes = [INT, LPVOID]
            self.play_lib.PlayM4_SetDisplayCallBack.restype = INT
            display_callback_type = CFUNCTYPE(None, LONG, POINTER(CHAR), LONG, LONG, LONG, LONG, LONG,
                                              LONG)
            # noinspection PyAttributeOutsideInit
            # 用于解决ctypes的回调函数中无法访问self的问题，详见
            # https://stackoverflow.com/questions/7259794/how-can-i-get-methods-to-work-as-callbacks-with-python-ctypes/65174074#65174074
            self.display_callback = display_callback_type(self._display_callback)
            if not self.play_lib.PlayM4_SetDisplayCallBack(self._get_play_control_port(), self.display_callback):
                self.error("设置播放回调函数失败")
            if not self.play_lib.PlayM4_Play(self._get_play_control_port(), None):
                self.error("开启播放失败" + str(self._get_play_control_port()))
        elif dwDataType == NET_DVR_STREAMDATA:
            self.play_lib.PlayM4_InputData.argtypes = [INT, POINTER(UNSIGNED_CHAR), UINT]
            self.play_lib.PlayM4_InputData.restype = INT
            if self.play_control_port is None:
                return
            if not self.play_lib.PlayM4_InputData(self.play_control_port, pBuffer, dwBufSize):
                pass
                # self.error("输入视频流错误")

    def get_ability(self):
        self.lib.NET_DVR_GetDeviceAbility.argtypes = [LONG, DWORD, CHAR_P, DWORD, CHAR_P, DWORD]
        self.lib.NET_DVR_GetDeviceAbility.restype = BOOL
        s = bytes("123"*2000, encoding=self.encoding)
        # ss = h_CHAR_P(s)
        out = bytes("123"*2000, encoding=self.encoding)
        if not self.lib.NET_DVR_GetDeviceAbility(self.user_id, 0x009, CHAR_P(s), len(s), out, len(out)):
            self.error("")

        a=  1


if __name__ == '__main__':
    camera = HIKCamera(ip="192.168.111.78", user_name="admin", password="12345678a")
    # camera.get_ability()
    config = camera.get_dvr_config()
    print(config.struDayNight.byDayNightFilterType)
    # print(config)
    # camera.set_dvr_config()
    # camera2.get_dvr_config()
    # camera2.start_preview(frame_buffer_size=10)

    # camera.set_real_data_callback()
    # camera.get_play_control_port()
    camera.start_preview(frame_buffer_size=10)
    while True:
        frame = camera.get_frame()
        print(frame.shape)
    # video = Path("/workspace/HiCamera/test.mp4")
    # camera.save_real_data(video)
    # time.sleep(3)

    # play_lib.PlayM4_Stop(0)
    # play_lib.PlayM4_CloseFile(0)
    # play_lib.PlayM4_FreePort(0)
    # camera.stop_preview()
    # camera.get_dvr_config()
    # camera.set_dvr_config()
    # camera.get_dvr_config()
