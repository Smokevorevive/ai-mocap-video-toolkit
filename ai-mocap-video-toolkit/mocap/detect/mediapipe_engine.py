"""MediaPipe fallback. CPU-only, no GPU required. Lower accuracy on fast motion."""
from __future__ import annotations

import numpy as np

from mocap.config.settings import DetectorSettings
from mocap.detect.base import COCO17, Keypoints2D

# MediaPipe Pose -> COCO-17 index remap.
_MP_TO_COCO = {0: 0, 2: 1, 5: 2, 7: 3, 8: 4, 11: 5, 12: 6, 13: 7, 14: 8,
               15: 9, 16: 10, 23: 11, 24: 12, 25: 13, 26: 14, 27: 15, 28: 16}


class MediaPipeDetector:
    name = "mediapipe"

    def __init__(self, cfg: DetectorSettings) -> None:
        import mediapipe as mp

        self._pose = mp.solutions.pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=cfg.score_threshold,
        )

    def detect(self, frames: list[tuple[int, np.ndarray]]) -> Keypoints2D:
        xy, conf, idx = [], [], []
        for fi, frame in frames:
            res = self._pose.process(frame[:, :, ::-1])
            if not res.pose_landmarks:
                xy.append(np.zeros((17, 2), dtype=np.float32))
                conf.append(np.zeros(17, dtype=np.float32))
            else:
                pts = np.array([[lm.x, lm.y] for lm in res.pose_landmarks.landmark])
                vis = np.array([lm.visibility for lm in res.pose_landmarks.landmark])
                xy.append(pts[[_MP_TO_COCO[i] for i in range(17)]])
                conf.append(vis[[_MP_TO_COCO[i] for i in range(17)]])
            idx.append(fi)
        return Keypoints2D(np.stack(xy), np.stack(conf), np.asarray(idx, dtype=np.int64))