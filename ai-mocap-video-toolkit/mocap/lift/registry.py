from __future__ import annotations

from mocap.config.settings import LiftSettings
from mocap.lift.base import Lifter


def build_lifter(cfg: LiftSettings) -> Lifter:
    if cfg.model == "motionbert":
        from mocap.lift.motionbert import MotionBERTLifter

        return MotionBERTLifter(cfg)
    if cfg.model == "videopose3d":
        from mocap.lift.videopose3d import VideoPose3DLifter

        return VideoPose3DLifter(cfg)
    if cfg.model == "hybrik":
        from mocap.lift.hybrik import HybriKLifter

        return HybriKLifter(cfg)
    raise ValueError(f"unknown lifter: {cfg.model}")