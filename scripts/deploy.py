"""
build脚本
"""
import shutil
import subprocess
from pathlib import Path

if __name__ == '__main__':
    project_dir = Path(__file__).parent.parent.resolve()
    # 删除build文件夹
    build_dir = Path(__file__).parent.parent.joinpath("build")
    shutil.rmtree(build_dir, ignore_errors=True)
    print(f"删除build文件夹{build_dir}")
    # 新建build文件夹
    build_dir.mkdir(parents=True, exist_ok=True)
    # 打包so
    subprocess.run(args=f"python -m nuitka --module --remove-output --no-pyi-file --include-package=camera ../camera",
                   shell=True,
                   check=True,
                   cwd=build_dir)
    # 复制测试脚本
    for script_name in []:
        shutil.copy(Path(__file__).parent.joinpath(script_name), build_dir.joinpath(script_name))
    # 复制依赖的库
    src_libs_dir = project_dir.joinpath("camera").joinpath("hik_vision").joinpath("libs")
    dst_libs_dir = build_dir.joinpath("camera").joinpath("hik_vision")
    dst_libs_dir.mkdir(parents=True)
    shutil.copytree(src_libs_dir, dst_libs_dir.joinpath("libs"))
    # 复制单元测试
    tests_dir = build_dir.joinpath("tests")
    tests_dir.mkdir(parents=True, exist_ok=True)
    for test_file_name in ["__init__.py", "test_hik_camera.py", "test_hik_h264_camera.py", "test_hik_h265_camera.py"]:
        test_file = project_dir.joinpath("tests").joinpath(test_file_name)
        if not test_file.exists():
            raise Exception(f"单元测试文件{test_file}不存在")
        shutil.copy(test_file, tests_dir.joinpath(test_file_name))
    # 复制第三方库
    name = "h264decoder.cpython-37m-x86_64-linux-gnu.so"
    shutil.copyfile(str(project_dir.joinpath(name)), str(build_dir.joinpath(name)))
    print(f"打包成功{build_dir}")


