"""Humanoid rig definition + loader. Rigs live in configs/rigs/*.json."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

RIG_DIR = Path(__file__).resolve().parents[2] / "configs" / "rigs"


@dataclass(frozen=True)
class RigBone:
    name: str
    parent: str | None
    offset: tuple[float, float, float]  # rest-pose offset in meters
    joint_idx: int                     # COCO-17 index it consumes


@dataclass(frozen=True)
class Rig:
    name: str
    bones: tuple[RigBone, ...]
    hip_height: float = 1.05

    def by_name(self, name: str) -> RigBone:
        for b in self.bones:
            if b.name == name:
                return b
        raise KeyError(name)


def load_rig(name: str) -> Rig:
    path = RIG_DIR / f"{name}.json"
    if not path.is_file():
        raise FileNotFoundError(f"rig not found: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    bones = tuple(
        RigBone(b["name"], b.get("parent"),
                tuple(float(x) for x in b["offset"]), int(b["joint_idx"]))
        for b in raw["bones"]
    )
    return Rig(raw["name"], bones, float(raw.get("hip_height", 1.05)))