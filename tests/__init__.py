from pathlib import Path

from camera import HIKCamera


def get_test_output_dir() -> Path:
    """
    获取测试输出文件夹
    :return:
    """
    test_output_dir = Path(__file__).parent.joinpath("output")
    test_output_dir.mkdir(exist_ok=True, parents=True)
    return test_output_dir


def get_test_output(file: str) -> Path:
    """
    获取测试输出
    :param file:
    :return:
    """
    return get_test_output_dir().joinpath(file)


def get_hik_camera() -> HIKCamera:
    """
    获取用于测试的海康相机
    :return:
    """
    return HIKCamera(ip="192.168.111.77", user_name="admin", password="12345678a")
