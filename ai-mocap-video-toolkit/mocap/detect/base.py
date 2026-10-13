"""Detector protocol + shared 2D keypoint container."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np

# COCO-17 joint order used across the whole toolkit.
COCO17 = (
    "nose", "left_eye", "right_eye", "left_ear", "right_ear",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle",
)


@dataclass
class Keypoints2D:
    xy: np.ndarray     # (T, J, 2) pixel coords
    conf: np.ndarray   # (T, J) confidence in [0, 1]
    frame_idx: np.ndarray  # (T,) source frame indices

    def __post_init__(self) -> None:
        if self.xy.shape[:2] != self.conf.shape:
            raise ValueError("xy/conf shape mismatch")
        if self.xy.shape[1] != len(COCO17):
            raise ValueError(f"expected {len(COCO17)} joints, got {self.xy.shape[1]}")


class Detector(Protocol):
    name: str

    def detect(self, frames: list[tuple[int, np.ndarray]]) -> Keypoints2D: ...