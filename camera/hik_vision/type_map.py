"""
海康数据类型与ctypes类型映射
"""

from ctypes import c_char, c_int, c_ulong, c_void_p, c_uint, c_char_p, c_ubyte, c_ushort, c_short, c_long, c_bool, \
    c_byte, c_uint16, c_float

BOOL = c_int
BYTE = c_ubyte
INT = c_int
UINT = c_uint
USHORT = c_ushort
LPVOID = c_void_p
HANDLE = c_void_p
HWND = c_void_p
WORD = c_ushort
CHAR = c_char
SHORT = c_short
LONG = c_int
DWORD = c_uint
UNSIGNED_CHAR = c_ubyte
UBYTE = c_ubyte
CHAR_P = c_char_p

# 上面的类型映射是根据海康的文档和ctypes的文档写的，但是用的时候有一些问题，下面的类型映射是来自于
# https://github.com/Rennbon/pyhikvision/blob/master/hkws/core/type_map.py
# 实际用的时候两套试一下，哪个好用用哪个
h_BOOL = c_bool
h_CHAR = c_char
h_BYTE = c_byte
h_INT = c_int
h_WORD = c_uint16
h_LONG = c_long
h_FLOAT = c_float
h_DWORD = c_ulong  # 64bit:c_ulong    32bit:c_uint32

h_VOID_P = c_void_p
h_HWND = c_void_p  # handle of window
h_CHAR_P = c_ubyte
h_BYTE_P =c_ubyte