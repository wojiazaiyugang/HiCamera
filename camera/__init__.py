from camera.data_class import Frame
from camera.encryption import verify_authorization
from camera.hik_vision import HIKCamera
from camera.utils.video_writer import VideoWriter

# ROOT_DIR = Path(__file__).parent.parent.resolve()
# verify_authorization(ROOT_DIR.joinpath("authorization.txt"))

__all__ = [
    "HIKCamera",  # 海康相机
    "Frame",  # 视频帧
    "VideoWriter",  # 视频写入器
]
