from camera.hik_vision import HIKCamera
from infer.encryption import verify_authorization

verify_authorization(ROOT_DIR.joinpath("authorization.txt"))

__all__ = [
    "HIKCamera"  # 海康相机
]
