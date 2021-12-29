"""
海康数据类型与ctypes类型映射
"""

from ctypes import c_bool, c_char, c_byte, c_int, c_uint16, c_long, c_float, c_ulong, c_void_p, c_ubyte, c_uint

h_BOOL = c_bool
h_CHAR = c_char
h_BYTE = c_byte
h_INT = c_int
h_UINT = c_uint
h_WORD = c_uint16
h_LONG = c_long
h_ULONG = c_ulong
h_FLOAT = c_float
h_DWORD = c_ulong  # 64bit:c_ulong    32bit:c_uint32
h_UNSIGNED_CHAR = c_ubyte
h_UBYTE = c_ubyte

h_VOID_P = c_void_p
h_HWND = c_void_p  # handle of window
h_CHAR_P = c_ubyte
h_BYTE_P = c_ubyte
h_UNSIGNED_CHAR_P = h_CHAR_P
