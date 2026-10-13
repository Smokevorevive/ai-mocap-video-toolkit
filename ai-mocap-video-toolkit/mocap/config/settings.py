"""Settings model + preset loading. Pydantic-validated, YAML-backed."""
from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field

Device = Literal["auto", "cpu", "cuda"]
PRESET_DIR = Path(__file__).resolve().parents[2] / "configs" / "presets"


class DetectorSettings(BaseModel):
    backend: Literal["rtmpose", "mediapipe", "vitpose"] = "rtmpose"
    score_threshold: float = Field(0.35, ge=0.0, le=1.0)
    max_persons: int = Field(1, ge=1, le=8)


class LiftSettings(BaseModel):
    model: Literal["motionbert", "videopose3d", "hybrik"] = "motionbert"
    window: int = Field(81, ge=9, le=243)
    smooth: float = Field(0.2, ge=0.0, le=1.0)


class RetargetSettings(BaseModel):
    rig: str = "humanoid_default"
    scale_mode: Literal["auto", "fixed", "hip_height"] = "hip_height"
    foot_lock: bool = True


class ExportSettings(BaseModel):
    formats: list[Literal["bvh", "glb", "fbx", "npz"]] = ["bvh", "glb"]
    fps_override: float | None = None


class Settings(BaseModel):
    preset: str = "default"
    device: Device = "auto"
    detector: DetectorSettings = DetectorSettings()
    lift: LiftSettings = LiftSettings()
    retarget: RetargetSettings = RetargetSettings()
    export: ExportSettings = ExportSettings()


def load_settings(preset: str = "default", device: str = "auto") -> Settings:
    """Load a preset YAML and merge CLI overrides. Missing preset -> defaults."""
    path = PRESET_DIR / f"{preset}.yaml"
    raw: dict = {}
    if path.is_file():
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    raw.setdefault("preset", preset)
    raw["device"] = device
    return Settings.model_validate(raw)