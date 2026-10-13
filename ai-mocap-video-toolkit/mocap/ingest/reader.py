"""Frame-accurate video reader with optional stride/downscale."""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

import cv2
import numpy as np


class VideoReader:
    """Yields BGR frames. `stride` skips frames but preserves source index."""

    def __init__(self, path: Path, stride: int = 1, max_width: int | None = 1280) -> None:
        if stride < 1:
            raise ValueError("stride must be >= 1")
        self.path = Path(path)
        self.stride = stride
        self.max_width = max_width

    def __iter__(self) -> Iterator[tuple[int, np.ndarray]]:
        cap = cv2.VideoCapture(str(self.path))
        if not cap.isOpened():
            raise RuntimeError(f"cannot open video: {self.path}")
        idx = 0
        try:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                if idx % self.stride == 0:
                    yield idx, self._maybe_scale(frame)
                idx += 1
        finally:
            cap.release()

    def _maybe_scale(self, frame: np.ndarray) -> np.ndarray:
        if not self.max_width or frame.shape[1] <= self.max_width:
            return frame
        scale = self.max_width / frame.shape[1]
        return cv2.resize(frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)