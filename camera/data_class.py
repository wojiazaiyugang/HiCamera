from typing import Optional
from datetime import datetime
from dataclasses import dataclass

import numpy as np


@dataclass()
class Frame:
    """
    数据帧
    """
    data: np.ndarray  # 数据帧 opencv格式
    frame_time: datetime  # 数据帧时间戳

