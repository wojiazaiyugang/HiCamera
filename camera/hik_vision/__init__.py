from ctypes import cdll, byref, c_char_p, CFUNCTYPE, POINTER
from pathlib import Path
from typing import List, Callable

from camera.hik_vision.type_map import h_LONG, h_DWORD, h_BYTE
from camera.hik_vision.structure import NET_DVR_USER_LOGIN_INFO, NET_DVR_DEVICEINFO_V40, NET_DVR_PREVIEWINFO


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
        self.encoding = "ascii"
        self.libs = self.read_libs()
        self.init_sdk()
        self.user_id = self._login(ip, user_name, password)
        self.preview_handle = None

    def __del__(self):
        self.clean_sdk()

    def call_cpp(self, func_name, *args):
        """
        调用so库
        :param func_name:
        :param args:
        :return:
        """
        for so_lib in self.libs:
            try:
                lib = cdll.LoadLibrary(so_lib)
                try:
                    value = eval("lib.%s" % func_name)(*args)
                    return value
                except Exception as e:
                    print('value except', e)
                    continue
            except Exception as e:
                print('loadlibrary except', e)
                continue
        raise Exception("没有找到接口！")

    @staticmethod
    def read_libs() -> List[str]:
        """
        读取所有so
        :return:
        """
        libs = []
        for file in Path(__file__).parent.joinpath("libs").iterdir():
            if file.name.endswith(".so"):
                libs.append(str(file))
        return libs

    def init_sdk(self):
        """
        初始化SDK
        :return:
        """
        if not self.call_cpp("NET_DVR_Init"):
            raise Exception(f"初始化失败：{self.get_last_error_code()}")

    def clean_sdk(self):
        """
        不再使用时清理相机
        :return:
        """
        if not self.call_cpp("NET_DVR_Cleanup"):
            raise Exception(f"清理SDK失败：{self.get_last_error_code()}")

    def get_last_error_code(self) -> int:
        return self.call_cpp("NET_DVR_GetLastError")

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
        user_id = self.call_cpp("NET_DVR_Login_V40", byref(user_login_info), byref(device_info))
        if user_id == -1:
            raise Exception(f"登录异常：{self.get_last_error_code()}")
        else:
            return user_id

    def get_sdk_version(self) -> str:
        """
        SDK版本信息，2个高字节表示主版本，2个低字节表示次版本。如0x00030000：表示版本为3.0。
        :return:
        """
        return hex(self.call_cpp("NET_DVR_GetSDKVersion"))

    def start_preview(self):
        """
        开始登预览
        :return:
        """
        preview_info = NET_DVR_PREVIEWINFO()
        preview_info.lChannel = 1
        preview_info.dwStreamType = 0
        preview_info.bBlocked = 1
        self.preview_handle = self.call_cpp("NET_DVR_RealPlay_V30", self.user_id, byref(preview_info), None, None)
        if self.preview_handle == -1:
            raise Exception(f"预览失败：{self.get_last_error_code()}")

    def stop_preview(self):
        """
        停止预览
        :return:
        """
        if not self.call_cpp("NET_DVR_StopRealPlay", self.preview_handle):
            raise Exception(f"停止预览异常：{self.get_last_error_code()}")

    def save_real_data(self, save_file: Path):
        """
        保存录像
        :return:
        """
        if not self.call_cpp("NET_DVR_SaveRealData", self.preview_handle, c_char_p(bytes(str(save_file), self.encoding))):
            raise Exception(f"保存录像异常：{self.get_last_error_code()}")

    def stop_save_real_data(self):
        """
        停止数据捕获
        :return:
        """
        if not self.call_cpp("NET_DVR_StopSaveRealData", self.preview_handle):
            raise Exception(f"停止数据捕获异常：{self.get_last_error_code()}")

    def set_real_data_callback(self, f: Callable):
        """
        注册实时码流回调数据
        :param preview_handle:
        :param f:
        :return:
        """
        real_data_callback = CFUNCTYPE(None, h_LONG, h_DWORD, POINTER(h_BYTE), h_DWORD, h_DWORD)
        cb = real_data_callback(f)
        if not self.call_cpp("NET_DVR_SetRealDataCallBack", self.preview_handle, cb, None):
            raise Exception(f"注册实时码流回调数据异常：{self.get_last_error_code()}")

    def set_standard_data_callback(self, f: Callable):
        """
        注册回调函数，捕获实时码流数据（标准码流）。
        """
        real_data_callback = CFUNCTYPE(None, h_LONG, h_DWORD, POINTER(h_BYTE), h_DWORD, h_DWORD)
        cb = real_data_callback(f)
        if not self.call_cpp("NET_DVR_SetStandardDataCallBack", self.preview_handle, cb, None):
            raise Exception(f"注册实时标准码流回调数据异常：{self.get_last_error_code()}")


if __name__ == '__main__':
    camera = HIKCamera(ip="192.168.230.81", user_name="admin", password="12345678a")
    # print(camera.get_last_error_code())
