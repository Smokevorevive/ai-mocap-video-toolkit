"""3D lifter protocol. Takes 2D keypoints, returns camera-relative 3D joints."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np

SKELETON_PARENTS = {
    0: None, 1: 0, 2: 0, 3: 1, 4: 2, 5: 0, 6: 0, 7: 5, 8: 6, 9: 7,
    10: 8, 11: 5, 12: 6, 13: 11, 14: 12, 15: 13, 16: 14,
}


@dataclass
class Pose3D:
    xyz: np.ndarray        # (T, J, 3) meters, root at hip midpoint
    conf: np.ndarray       # (T, J)
    fps: float

    def root_relative(self) -> "Pose3D":
        root = (self.xyz[:, 11] + self.xyz[:, 12]) / 2.0
        return Pose3D(self.xyz - root[:, None, :], self.conf, self.fps)


class Lifter(Protocol):
    name: str

    def lift(self, kp2d, fps: float) -> Pose3D: ...