"""
SDK加密
"""
import getpass
from pathlib import Path
from typing import Optional

from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

key = "This is the key of the HiCamera "
# noinspection SpellCheckingInspection
iv = " wojiazaiyugang "


def get_device_uuid() -> str:
    """
    获取设备UUID作为设备唯一标识
    :return:
    """
    with open("/sys/class/dmi/id/product_uuid", "r") as f:
        return f.read().rstrip()


def pad_text(text: str) -> bytes:
    """
    待加密数据补足长度为16的倍数
    :param text:
    :return:
    """
    pad_count = 16 - (len(text.encode("utf-8")) % 16)
    text = text + "\0" * pad_count
    return text.encode("utf-8")


def encrypt(text: str) -> str:
    """
    AES加密
    :param text:
    :return:
    """
    text = pad_text(text)
    cryptos = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
    cipher_text = cryptos.encrypt(text)
    return b2a_hex(cipher_text).decode("utf-8")


def decrypt(text: str) -> Optional[str]:
    """
    解密
    :param text:
    :return:
    """
    cryptos = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
    # noinspection PyBroadException
    try:
        plain_text = cryptos.decrypt(a2b_hex(text))
        return bytes.decode(plain_text).rstrip('\0')
    except Exception:
        return None


def generate_authorization_file(file: Path):
    """
    生成授权文件
    :param file:
    :return:
    """
    uuid = get_device_uuid()
    input_key = getpass.getpass(f"设备编号：{uuid}，输入授权密钥:")
    if input_key != key:
        raise Exception(f"授权密钥错误")
    with open(file, "w") as f:
        f.write(encrypt(uuid))
    print(f"授权成功")


def verify_authorization(file: Path):
    """
    校验授权
    :param file: 要校验的授权文件，不存在或者校验失败时
    需要重新输入密钥生成授权文件，校验成功则放行
    :return:
    """
    if not file.exists():
        generate_authorization_file(file)
    with open(file, "r") as f:
        code = f.read().strip()
        uuid = get_device_uuid()
        authorization_code = encrypt(uuid)
        if code != authorization_code:
            raise Exception(f"密钥匹配错误，授权失败")


if __name__ == '__main__':
    print(encrypt("4a98f118-ccd4-4343-00de-049226bed249"))
#     uuid = get_device_uuid()
#     print(uuid)
#     code = encrypt(uuid)
#     print(code)
#     print(decrypt(code) == uuid)
