from pathlib import Path


def get_scripts_output(file: str) -> Path:
    """
    获取脚本输出文件路径
    :param file:
    :return:
    """
    scripts_output_dir = Path(__file__).with_name("output")
    scripts_output_dir.mkdir(parents=True, exist_ok=True)
    return scripts_output_dir.joinpath(file)
