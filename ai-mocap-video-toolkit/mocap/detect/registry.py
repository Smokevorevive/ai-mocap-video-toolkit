"""Detector factory. Backends are imported lazily to keep startup cheap."""
from __future__ import annotations

from mocap.config.settings import DetectorSettings
from mocap.detect.base import Detector


def build_detector(cfg: DetectorSettings) -> Detector:
    if cfg.backend == "mediapipe":
        from mocap.detect.mediapipe_engine import MediaPipeDetector

        return MediaPipeDetector(cfg)
    if cfg.backend == "rtmpose":
        from mocap.detect.rtmpose_engine import RTMPoseDetector

        return RTMPoseDetector(cfg)
    if cfg.backend == "vitpose":
        from mocap.detect.vitpose_engine import ViTPoseDetector

        return ViTPoseDetector(cfg)
    raise ValueError(f"unknown detector backend: {cfg.backend}")