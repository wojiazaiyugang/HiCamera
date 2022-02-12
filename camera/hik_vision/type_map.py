"""
海康数据类型与ctypes类型映射
"""

from ctypes import c_bool, c_char, c_int, c_float, c_ulong, c_void_p, c_uint, c_char_p, c_ubyte, c_ushort, c_short, POINTER

BOOL = c_int
# h_CHAR = c_char
BYTE = c_ubyte
INT = c_int
UINT = c_uint
USHORT = c_ushort
LPVOID = c_void_p
HANDLE = c_void_p
HWND = c_void_p
LPDWORD = POINTER(c_uint)
WORD = c_ushort
CHAR = c_char
SHORT = c_short
LONG = c_int
# h_ULONG = c_ulong
# h_FLOAT = c_float
DWORD = c_uint
UNSIGNED_CHAR = c_ubyte
UBYTE = c_ubyte
#
# h_VOID_P = c_void_p
# h_HWND = c_void_p  # handle of window
CHAR_P = c_char_p
# h_BYTE_P = c_ubyte
# h_UNSIGNED_CHAR_P = h_CHAR_P
