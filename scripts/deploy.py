"""
build脚本
"""
import os
import shutil
from pathlib import Path

if __name__ == '__main__':
    project_dir = Path(__file__).parent.parent.resolve()
    # 删除build文件夹
    build_dir = Path(__file__).parent.parent.joinpath("build").joinpath("HiCamera")
    shutil.rmtree(build_dir, ignore_errors=True)
    print(f"删除build文件夹{build_dir}")
    # 新建build文件夹
    build_dir.mkdir(parents=True, exist_ok=True)
    # 打包so
    os.chdir(build_dir)
    os.system(f"python -m nuitka --module --remove-output --no-pyi-file --include-package=camera ../../camera")
    # 复制测试脚本
    for script_name in ["real_data.py", "save_video.py"]:
        shutil.copy(Path(__file__).parent.joinpath(script_name), build_dir.joinpath(script_name))
    # 复制依赖的库
    src_libs_dir = project_dir.joinpath("camera").joinpath("hik_vision").joinpath("libs")
    dst_libs_dir = build_dir.joinpath("camera").joinpath("hik_vision")
    dst_libs_dir.mkdir(parents=True)
    shutil.copytree(src_libs_dir, dst_libs_dir.joinpath("libs"))
    print(f"打包成功{build_dir}")


