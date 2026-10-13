"""Sidecar metadata: writes a manifest.json next to each run."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class RunManifest:
    source: str
    fps: float
    frame_count: int
    stride: int
    preset: str
    device: str
    version: str
    exports: list[str]

    def write(self, out_dir: Path) -> Path:
        out_dir.mkdir(parents=True, exist_ok=True)
        target = out_dir / "manifest.json"
        target.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
        return target