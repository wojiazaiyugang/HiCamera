"""
demo示例
"""
from ctypes import c_byte, memmove

from camera import HIKCamera


# noinspection PyPep8Naming
def real_data_callback(lRealHandle,
                       dwDataType,
                       pBuffer,
                       dwBufSize,
                       dwUser):
    """
    实时数据回调函数
    :param lRealHandle:
    :param dwDataType:
    :param pBuffer:
    :param dwBufSize:
    :param dwUser:
    :return:
    """
    if dwDataType == 1:
        print("头数据")
    if dwDataType == 2:
        print("流数据")
    if dwDataType == 4:
        print("标准视频流数据")
    if dwDataType == 5:
        print("标准音频流数据")
    if dwDataType == 112:
        print("私有数据")
    if dwBufSize > 0:
        res = bytearray(dwBufSize)
        rptr = (c_byte * dwBufSize).from_buffer(res)
        if not memmove(rptr, pBuffer, dwBufSize):
            raise RuntimeError("memmove failed")
        print(res.hex())


if __name__ == '__main__':
    hik_camera = camera = HIKCamera(ip="192.168.230.81", user_name="admin", password="12345678a")
