import os
import time
from ctypes import cdll, byref, c_char_p, CFUNCTYPE, POINTER, string_at, sizeof
from datetime import datetime
from pathlib import Path
from typing import Any, List

import numpy as np

from camera.data_class import Frame
from camera.hik_vision.structure import NET_DVR_USER_LOGIN_INFO, NET_DVR_DEVICEINFO_V40, NET_DVR_PREVIEWINFO, \
    NET_DVR_CAMERAPARAMCFG, NET_DVR_VIDEOEFFECT, NET_DVR_GAIN, \
    NET_DVR_WHITEBALANCE, NET_DVR_GAMMACORRECT, NET_DVR_EXPOSURE, NET_DVR_WDR, NET_DVR_DAYNIGHT, NET_DVR_NOISEREMOVE, \
    NET_DVR_CMOSMODECFG, NET_DVR_TIME, NET_DVR_BACKLIGHT, \
    NET_DVR_LOCAL_SDK_PATH, NET_DVR_SYSHEAD, NET_DVR_STREAMDATA, NET_DVR_AUDIOSTREAMDATA, NET_DVR_PRIVATE_DATA, \
    NET_DVR_COMPRESSIONCFG_V30, NET_DVR_PACKET_INFO_EX
from camera.hik_vision.type_map import LONG, DWORD, BYTE, BOOL, LPVOID, UBYTE, CHAR, INT, UINT, UNSIGNED_CHAR, CHAR_P

import PyNvCodec as nvc


class HIKCamera:
    """
    海康相机
    """

    def __init__(self, ip: str,
                 user_name: str,
                 password: str,
                 gpu_index: int = 0):
        """
        相机初始化
        :param ip: 相机IP
        :param user_name: 用户名
        :param password: 密码
        :param 实时视频流解码用的GPU索引，默认为0
        """
        self.ip = ip
        self.user_name = user_name
        self.password = password
        self.encoding = "utf-8"
        self.user_id = None
        libs_dir = Path(__file__).parent.joinpath("libs")
        os.chdir(libs_dir)
        self.lib = cdll.LoadLibrary(str(libs_dir.joinpath("libhcnetsdk.so")))
        self.lib.NET_DVR_Init.argtypes = []
        self.lib.NET_DVR_Init.restype = BOOL
        if not self.lib.NET_DVR_Init():
            raise Exception(f"初始化失败：{self._get_last_error_code()}")
        self.play_lib = cdll.LoadLibrary(str(libs_dir.joinpath("libPlayCtrl.so")))
        self.channel = None  # 通道号
        self.user_id = self._login(ip, user_name, password)
        # print(f"user id is {self.user_id}")
        self.preview_handle = None
        self.play_control_port = None  # 播放通道号
        self.frames: List[Frame] = []  # frame buffer
        self.frame_buffer_size = None

        cfg = self.get_compress_config()
        self.width, self.height = {
            19: (1280, 720),
            27: (1920, 1080),
            64: (3840, 2160),
            70: (2560, 1440),
            115: (3840, 2400),
        }.get(cfg.struNormHighRecordPara.byResolution, (0, 0))
        if self.width == 0 or self.height == 0:
            print(f"该分辨率只能保存视频，无法获取实时视频流")
        self.gpu_index = gpu_index
        self.nv_dec = nvc.PyNvDecoder(self.width, self.height, nvc.PixelFormat.NV12, nvc.CudaVideoCodec.H264,
                                      self.gpu_index)
        self.nv_cvt_nv12_to_bgr = nvc.PySurfaceConverter(self.width, self.height, self.nv_dec.Format(),
                                                         nvc.PixelFormat.BGR,
                                                         self.gpu_index)
        self.nv_dwn = nvc.PySurfaceDownloader(self.width, self.height, self.nv_cvt_nv12_to_bgr.Format(), self.gpu_index)
        self.recording = False  # 正在保存录像

    def __del__(self):
        self._logout()
        self._clean_sdk()

    def _logout(self):
        """
        登出
        :return:
        """
        if self.user_id is None:
            return
        self.lib.NET_DVR_Logout.argtypes = [LONG]
        self.lib.NET_DVR_Logout.restype = BOOL
        if not self.lib.NET_DVR_Logout(self.user_id):
            self._error(f"登出错误")

    def _clean_sdk(self):
        """
        不再使用时清理相机
        :return:
        """
        self.lib.NET_DVR_Cleanup.argtypes = []
        self.lib.NET_DVR_Cleanup.restype = BOOL
        if not self.lib.NET_DVR_Cleanup():
            raise Exception(f"清理SDK失败：{self._get_last_error_code()}")

    def _get_last_error_code(self) -> int:
        """
        操作出错，获取上一次的出错信息
        :return:
        """
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
            raise Exception(f"登录异常：{self._get_last_error_code()}")
        else:
            self.channel = device_info.struDeviceV30.byStartChan
            return user_id

    def _real_play_callback(self, lPreviewHandle, pstruPackInfo: NET_DVR_PACKET_INFO_EX, pUser):
        data = string_at(pstruPackInfo.contents.pPacketBuffer, pstruPackInfo.contents.dwPacketSize)
        enc_packet = np.frombuffer(data, dtype=np.uint8)
        pkt_data = nvc.PacketData()
        raw_surface = self.nv_dec.DecodeSurfaceFromPacket(enc_packet, pkt_data)
        if not raw_surface.Empty():
            cc_ctx = nvc.ColorspaceConversionContext(color_space=nvc.ColorSpace.BT_709,
                                                     color_range=nvc.ColorRange.MPEG)
            cvt_surface = self.nv_cvt_nv12_to_bgr.Execute(raw_surface, cc_ctx)
            raw_frame = np.ndarray(shape=(cvt_surface.HostSize()), dtype=np.uint8)
            self.nv_dwn.DownloadSingleSurface(cvt_surface, raw_frame)
            frame_data = raw_frame.reshape((self.height, self.width, 3))
            frame_time = datetime(year=pstruPackInfo.contents.dwYear,
                                  month=pstruPackInfo.contents.dwMonth,
                                  day=pstruPackInfo.contents.dwDay,
                                  hour=pstruPackInfo.contents.dwHour,
                                  minute=pstruPackInfo.contents.dwMinute,
                                  second=pstruPackInfo.contents.dwSecond,
                                  microsecond=pstruPackInfo.contents.dwMillisecond * 1000)
            self.frames.append(Frame(data=frame_data, frame_time=frame_time))
            if self.frame_buffer_size and len(self.frames) > self.frame_buffer_size:
                del self.frames[0]

    def start_preview(self, frame_buffer_size: int = None) -> int:
        """
        开始预览
        :arg frame_buffer_size 实时数据的buffer size。0或者None标识不缓存帧。
        注意：如果开启了frame_buffer_size，会注册回调函数，python无法进行自动垃圾回收，即使手动del和gc也会内存泄漏，见下面的例子

        camera = HIKCamera(ip="192.168.111.78", user_name="admin", password="12345678a")
        camera.start_preview(frame_buffer_size=10)
        while True:
            time.sleep(2)
        camera.stop_preview()
        del camera
        gc.collect()

        必须手动调用del和gc，这样多次登录相机才不会报错，但是即使这样，pyhton这端仍会内存泄漏，因此应避免多次初始化
        :return:
        """
        self.frame_buffer_size = frame_buffer_size
        preview_info = NET_DVR_PREVIEWINFO()
        preview_info.lChannel = self.channel
        preview_info.dwStreamType = 0
        preview_info.bBlocked = 1
        # real_data_callback_type = CFUNCTYPE(None, LONG, DWORD, POINTER(BYTE), DWORD, LPVOID)
        # noinspection PyAttributeOutsideInit
        # 见standard_real_data_callback中的注释
        # if frame_buffer_size:
        #     self.standard_real_data_callback = real_data_callback_type(self._standard_real_data_callback)
        # else:
        #     # noinspection PyAttributeOutsideInit
        #     self.standard_real_data_callback = None
        self.lib.NET_DVR_RealPlay_V40.argtypes = [LONG, POINTER(NET_DVR_PREVIEWINFO), LPVOID, LPVOID]
        self.lib.NET_DVR_RealPlay_V40.restype = LONG
        self.preview_handle = self.lib.NET_DVR_RealPlay_V40(self.user_id, byref(preview_info), None, None)
        if self.preview_handle == -1:
            raise Exception(f"预览失败：{self._get_last_error_code()}")
        if frame_buffer_size:
            cfg = self.get_compress_config()
            if cfg.struNormHighRecordPara.byVideoEncType != 1:
                raise Exception(f"获取实时视频流目前只支持H264编码")
            self.lib.NET_DVR_SetESRealPlayCallBack.argtypes = [LONG, LPVOID, LPVOID]
            self.lib.NET_DVR_SetESRealPlayCallBack.restype = BOOL
            callback_type = CFUNCTYPE(None, LONG, POINTER(NET_DVR_PACKET_INFO_EX), LPVOID)
            # 用于解决ctypes的回调函数中无法访问self的问题，详见
            # https://stackoverflow.com/questions/7259794/how-can-i-get-methods-to-work-as-callbacks-with-python-ctypes/65174074#65174074
            # noinspection PyAttributeOutsideInit
            self._real_play_callback = callback_type(self._real_play_callback)
            if not self.lib.NET_DVR_SetESRealPlayCallBack(self.preview_handle, self._real_play_callback, LPVOID()):
                self._error("实时数据回调错误")
        return self.preview_handle

    def _stop_real_data_callback(self):
        """
        停止实时回调
        :return:
        """
        if not self.lib.NET_DVR_SetESRealPlayCallBack(self.preview_handle, None, LPVOID()):
            self._error("停止实时数据回调错误")

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
        if self.preview_handle is None:
            raise Exception(f"没有开启预览")
        self.lib.NET_DVR_StopRealPlay.argtypes = [LONG]
        self.lib.NET_DVR_StopRealPlay.restype = BOOL
        if self.frame_buffer_size:
            self._stop_real_data_callback()
        if not self.lib.NET_DVR_StopRealPlay(self.preview_handle):
            self._error("停止预览异常")

    def save_real_data(self, save_file: Path, stream_type: int = 2):
        """
        保存录像
        :param save_file: 保存文件路径
        :param stream_type: 保存流类型
        1: mp4v
        2: avc1
        :return:
        """
        if self.preview_handle is None:
            self._error("相机未启动预览，无法保存视频")
        if self.recording:
            self._error("已经在录像中，无法再次录像")
        self.lib.NET_DVR_SaveRealData_V30.argtypes = [LONG, DWORD, POINTER(CHAR)]
        self.lib.NET_DVR_SaveRealData_V30.restype = BOOL
        if not self.lib.NET_DVR_SaveRealData_V30(self.preview_handle, stream_type,
                                                 c_char_p(bytes(str(save_file), self.encoding))):
            self._error("保存录像异常")
        self.recording = True

    def stop_save_real_data(self):
        """
        停止数据捕获
        :return:
        """
        if not self.recording:
            self._error("没有在保存录像")
        self.lib.NET_DVR_StopSaveRealData.argtypes = [LONG]
        self.lib.NET_DVR_StopSaveRealData.restype = BOOL
        if not self.lib.NET_DVR_StopSaveRealData(self.preview_handle):
            self._error("停止录像异常")
        self.recording = False

    def _get_dvr_config(self, command: int, cfg: Any) -> Any:
        """
        获取设备的配置信息
        :return:
        """
        self.lib.NET_DVR_GetDVRConfig.argtypes = [LONG, DWORD, LONG, LPVOID, DWORD, POINTER(DWORD)]
        self.lib.NET_DVR_GetDVRConfig.restype = BOOL
        if not self.lib.NET_DVR_GetDVRConfig(self.user_id, command, self.channel, byref(cfg), sizeof(cfg),
                                             byref(DWORD(0))):
            self._error(f"获取设备配置信息失败，command={command}， cfg={cfg}")
        return cfg

    def _set_dvr_config(self, command: int, cfg: Any):
        """
        设置参数
        :param cfg:
        :return:
        """
        self.lib.NET_DVR_SetDVRConfig.argtypes = [LONG, DWORD, LONG, LPVOID, DWORD]
        self.lib.NET_DVR_SetDVRConfig.restype = BOOL
        if not self.lib.NET_DVR_SetDVRConfig(self.user_id, command, self.channel, byref(cfg), sizeof(cfg)):
            self._error(f"设置参数失败，command={command}，cfg={cfg}")

    def get_ccd_config(self) -> NET_DVR_CAMERAPARAMCFG:
        """
        获取前端参数
        :return:
        """
        return self._get_dvr_config(1067, NET_DVR_CAMERAPARAMCFG())

    def set_ccd_config(self, cfg: NET_DVR_CAMERAPARAMCFG):
        """
        设置前端参数
        :param cfg:
        :return:
        """
        self._set_dvr_config(1068, cfg)

    def get_compress_config(self) -> NET_DVR_COMPRESSIONCFG_V30:
        """
        获取图像压缩参数
        :return:
        """
        return self._get_dvr_config(1040, NET_DVR_COMPRESSIONCFG_V30())

    def set_compress_config(self, cfg: NET_DVR_COMPRESSIONCFG_V30):
        """
        设置图像压缩参数
        :param cfg:
        :return:
        """
        self._set_dvr_config(1041, cfg)

    def get_frame(self) -> Frame:
        """
        读一帧图片
        :return:
        """
        while len(self.frames) < 1:
            time.sleep(0.001)
        frame = self.frames[0]
        del self.frames[0]
        return frame

    def _error(self, reason: str):
        """
        报错
        :param reason:
        :return:
        """
        error_code = self._get_last_error_code()
        if error_code != 0:
            raise Exception(f"相机{self.ip} {reason}，错误码：{error_code}")

    def ptz_control(self, command: int, command_type: int, speed: int):
        """
        云台控制
        :param command_type: 0 - 开始执行命令 1 - 停止执行命令
        :param command:
        11：焦距变大（倍率变大）
        12：焦距变小（倍率变小）
        21：云台上仰
        22：云台下俯
        23：云台左转
        24：云台右转

        :param speed: 云台速度，1-7
        :return:
        """
        self.lib.NET_DVR_PTZControlWithSpeed_Other.argtypes = [LONG, LONG, DWORD, DWORD, DWORD]
        self.lib.NET_DVR_PTZControlWithSpeed_Other.restype = BOOL
        res = self.lib.NET_DVR_PTZControlWithSpeed_Other(self.user_id, self.channel, command, command_type, speed)
        if not res:
            self._error("云台控制错误")


if __name__ == '__main__':
    camera = HIKCamera(ip="192.168.111.75", user_name="admin", password="12345678a")
    camera.start_preview()
    video = Path("/workspace/HiCamera/test.mp4")
    camera.save_real_data(video)
    for i in range(2):
        camera.ptz_control(command=11, command_type=0, speed=1)
        time.sleep(2)
        camera.ptz_control(command=11, command_type=1, speed=1)

        camera.ptz_control(command=21, command_type=0, speed=1)
        time.sleep(2)
        camera.ptz_control(command=21, command_type=1, speed=1)

        camera.ptz_control(command=22, command_type=0, speed=1)
        time.sleep(2)
        camera.ptz_control(command=22, command_type=1, speed=1)

        camera.ptz_control(command=23, command_type=0, speed=1)
        time.sleep(5)
        camera.ptz_control(command=23, command_type=1, speed=1)

        camera.ptz_control(command=24, command_type=0, speed=1)
        time.sleep(10)
        camera.ptz_control(command=24, command_type=1, speed=1)

        camera.ptz_control(command=12, command_type=0, speed=1)
        time.sleep(2)
        camera.ptz_control(command=12, command_type=1, speed=1)
    camera.stop_save_real_data()
    camera.start_preview()
    # camera.get_ability()
    # config = camera._get_dvr_config()
    # print(config.struDayNight.byDayNightFilterType)
    # print(config)
    # camera.set_dvr_config()
    # camera2.get_dvr_config()
    # camera2.start_preview(frame_buffer_size=10)

    # camera.set_real_data_callback()
    # camera.get_play_control_port()
    # camera.start_preview(frame_buffer_size=10)
    # config = camera.get_ccd_config()
    # config.struDayNight.byDayNightFilterType = 0  # 白天
    # camera.set_ccd_config(config)

    # time.sleep(1)

    # play_lib.PlayM4_Stop(0)
    # play_lib.PlayM4_CloseFile(0)
    # play_lib.PlayM4_FreePort(0)
    # camera.stop_preview()
    # camera.get_dvr_config()
    # camera.set_dvr_config()
    # camera.get_dvr_config()
