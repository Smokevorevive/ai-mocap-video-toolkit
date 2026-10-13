"""Output driver dispatch. Each writer takes (rotations, rig, pose, fps, out)."""
from __future__ import annotations

from pathlib import Path

from mocap.lift.base import Pose3D
from mocap.retarget.rig import Rig


def export_all(
    formats: list[str],
    rotations: dict,
    rig: Rig,
    pose: Pose3D,
    fps: float,
    out_dir: Path,
) -> list[str]:
    out_dir.mkdir