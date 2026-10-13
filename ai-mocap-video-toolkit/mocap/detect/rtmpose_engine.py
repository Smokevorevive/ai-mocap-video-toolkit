"""RTMPose ONNX detector. Fast, accurate, 17 COCO joints."""
from __future__ import annotations

import numpy as np

from mocap.config.settings import DetectorSettings
from mocap.detect.base import Keypoints2D
from mocap.models.weights import ensure_weights
from mocap.utils.onnx import OrtSession


class RTMPoseDetector:
    name = "rtmpose"

    def __init__(self, cfg: DetectorSettings) -> None:
        self.cfg = cfg
        ckpt = ensure_weights("rtmpose-m.onnx")
        self.session = OrtSession(ckpt, prefer_cuda=True)

    def detect(self, frames: list[tuple[int, np.ndarray]]) -> Keypoints2D:
        xy, conf, idx = [], [], []
        for fi, frame in frames:
            kp, sc = self._one(frame)
            xy.append(kp)
            conf.append(sc)
            idx.append(fi)
        return Keypoints2D(np.stack(xy), np.stack(conf), np.asarray(idx, dtype=np.int64))

    def _one(self, frame: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        # NOTE: RTMPose expects letterboxed 256x192 input, BGR->RGB, /255.
        h, w = frame.shape[:2]
        inp = self._preprocess(frame)
        out = self.session.run(inp)[0]  # (1, 17, 2) simcc or heatmap-decoded
        kp = out.reshape(17, 2)
        sc = np.full(17, 0.9, dtype=np.float32)
        return kp, sc  # TODO(perf): decode simcc per-joint confidence

    def _preprocess(self, frame: np.ndarray) -> np.ndarray:
        import cv2

        resized = cv2.resize(frame, (192, 256), interpolation=cv2.INTER_LINEAR)
        rgb = resized[:, :, ::-1].astype(np.float32) / 255.0
        return rgb.transpose(2, 0, 1)[None]