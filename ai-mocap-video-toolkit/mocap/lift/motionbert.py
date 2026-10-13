"""MotionBERT-style temporal lifter. Sliding window over 2D sequence."""
from __future__ import annotations

import numpy as np
from scipy.signal import savgol_filter

from mocap.config.settings import LiftSettings
from mocap.lift.base import Keypoints2D, Pose3D  # noqa: F401  (re-exported)
from mocap.models.weights import ensure_weights
from mocap.utils.onnx import OrtSession


class MotionBERTLifter:
    name = "motionbert"

    def __init__(self, cfg: LiftSettings) -> None:
        self.cfg = cfg
        self.window = cfg.window
        ckpt = ensure_weights("motionbert-lite.onnx")
        self.session = OrtSession(ckpt, prefer_cuda=True)

    def lift(self, kp2d, fps: float) -> Pose3D:
        norm = self._normalize(kp2d.xy)
        xyz = self._sliding(norm)
        xyz = self._smooth(xyz)
        return Pose3D(xyz=xyz, conf=kp2d.conf, fps=fps)

    def _normalize(self, xy: np.ndarray) -> np.ndarray:
        # Root at hip midpoint, scale by torso length. Keeps lifter scale-invariant.
        root = (xy[:, 11] + xy[:, 12]) / 2.0
        torso = np.linalg.norm(xy[:, 5] - xy[:, 12], axis=-1, keepdims=True) + 1e-6
        return (xy - root[:, None, :]) / torso[:, None, :]

    def _sliding(self, norm: np.ndarray) -> np.ndarray:
        T = norm.shape[0]
        pad = self.window // 2
        padded = np.pad(norm, ((pad, pad), (0, 0), (0, 0)), mode="edge")
        out = np.zeros((T, norm.shape[1], 3), dtype=np.float32)
        for t in range(T):
            chunk = padded[t : t + self.window].transpose(2, 0, 1)[None]
            out[t] = self.session.run(chunk)[0].reshape(norm.shape[1], 3)
        return out

    def _smooth(self, xyz: np.ndarray) -> np.ndarray:
        if xyz.shape[0] < 9 or self.cfg.smooth <= 0:
            return xyz
        win = min(15, xyz.shape[0] - (1 - xyz.shape[0] % 2))
        return savgol_filter(xyz, win, 3, axis=0).astype(np.float32)