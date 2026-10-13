"""Rotation solver. Computes per-bone quaternions from 3D joint positions."""
from __future__ import annotations

import numpy as np

from mocap.lift.base import Pose3D
from mocap.retarget.rig import Rig


def solve_rotations(pose: Pose3D, rig: Rig, foot_lock: bool = True) -> dict[str, np.ndarray]:
    """Return {bone_name: (T, 4) quaternion} in world space, Y-up, meters.

    Bone direction is derived from the consuming joint's child offset in the rig.
    Foot lock zeroes X/Z translation on ankle bones to kill foot slide.
    """
    T = pose.xyz.shape[0]
    out: dict[str, np.ndarray] = {}
    for bone in rig.bones:
        parent = rig.by_name(bone.parent) if bone.parent else None
        cur = pose.xyz[:, bone.joint_idx]
        par = pose.xyz[:, parent.joint_idx] if parent else np.zeros_like(cur)
        vec = cur - par
        if foot_lock and bone.name.startswith("shin"):
            vec[:, 0] = 0.0
            vec[:, 2] = 0.0
        out[bone.name] = _vec_to_quat(vec, rest=np.asarray(bone.offset, dtype=np.float32))
    return out


def _vec_to_quat(vec: np.ndarray, rest: np.ndarray) -> np.ndarray:
    """Shortest-arc quaternion taking `rest` to `vec`, per frame."""
    rest = rest / (np.linalg.norm(rest) + 1e-8)
    v = vec / (np.linalg.norm(vec, axis=-1, keepdims=True) + 1e-8)
    dot = np.clip(v @ rest, -1.0, 1.0)
    cross = np.cross(np.broadcast_to(rest, v.shape), v)
    w = 1.0 + dot
    q = np.concatenate([w[:, None], cross], axis=-1)
    return q / (np.linalg.norm(q, axis=-1, keepdims=True) + 1e-8)