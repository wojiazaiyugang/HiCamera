from pathlib import Path

from camera.hik_vision import HIKCamera
from camera.encryption import verify_authorization

ROOT_DIR = Path(__file__).parent.parent.resolve()
verify_authorization(ROOT_DIR.joinpath("authorization.txt"))

__all__ = [
    "HIKCamera"  # 海康相机
]
