"""VideoPose3D lifter. Per-frame MLP, no temporal context. Fast, jittery."""
from __future__ import annotations

import numpy as np

from mocap.config.settings import LiftSettings
from mocap.lift.base import Pose3D
from mocap.models.weights import ensure_weights
from mocap.utils.onnx import OrtSession


class VideoPose3DLifter:
    name = "videopose3d"

    def __init__(self, cfg: LiftSettings) -> None:
        self.cfg = cfg
        self.session = OrtSession(ensure_weights("videopose3d.onnx"), prefer_cuda=True)

    def lift(self, kp2d, fps: float) -> Pose3D:
        xyz = np.zeros((kp2d.xy.shape[0], kp2d.xy.shape[1], 3), dtype=np.float32)
        for t in range(kp2d.xy.shape[0]):
            feat = kp2d.xy[t].reshape(1, -1, 1).transpose(0, 2, 1)
            xyz[t] = self.session.run(feat)[0].reshape(kp2d.xy.shape[1], 3)
        return Pose3D(xyz, kp2d.conf, fps).root_relative()