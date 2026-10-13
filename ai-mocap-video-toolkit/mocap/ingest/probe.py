"""Container/codec probe. Uses cv2 first, falls back to ffprobe."""
from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import cv2


@dataclass(frozen=True)
class VideoInfo:
    path: Path
    width: int
    height: int
    fps: float
    frame_count: int
    codec: str

    def as_table(self) -> str:
        dur = self.frame_count / self.fps if self.fps else 0.0
        return (
            f"{self.path.name}\n"
            f"  {self.width}x{self.height} @ {self.fps:.3f} fps\n"
            f"  frames={self.frame_count} ~{dur:.2f}s codec={self.codec}"
        )


def probe_video(path: Path) -> VideoInfo:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError(f"cannot open video: {path}")
    try:
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = float(cap.get(cv2.CAP_PROP_FPS)) or 30.0
        count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
        codec = "".join(chr((fourcc >> (8 * i)) & 0xFF) for i in range(4)).strip() or "unknown"
    finally:
        cap.release()

    if count <= 0 and shutil.which("ffprobe"):
        count = _ffprobe_frame_count(path)
    return VideoInfo(path, width, height, fps, count, codec)


def _ffprobe_frame_count(path: Path) -> int:
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-count_frames", "-show_entries", "stream=nb_read_frames",
             "-of", "json", str(path)],
            capture_output=True, text=True, timeout=30, check=True,
        ).stdout
        streams = json.loads(out).get("streams") or [{}]
        return int(streams[0].get("nb_read_frames", 0))
    except (subprocess.SubprocessError, ValueError, json.JSONDecodeError):
        return 0