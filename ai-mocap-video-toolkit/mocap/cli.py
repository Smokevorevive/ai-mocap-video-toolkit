"""CLI entrypoint. `mocap run <video>` drives the full pipeline."""
from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from mocap.config.settings import load_settings
from mocap.pipeline.orchestrator import JobOrchestrator
from mocap.utils.logging import setup_logging

app = typer.Typer(add_completion=False, no_args_is_help=True, help="AI motion capture from video.")
console = Console()


@app.command()
def run(
    video: Path = typer.Argument(..., exists=True, dir_okay=False, help="Input footage (mp4/mov/mkv)."),
    out: Path = typer.Option(Path("runs/latest"), "--out", "-o", help="Output directory."),
    preset: str = typer.Option("default", "--preset", help="Pipeline preset name."),
    device: str = typer.Option("auto", "--device", help="auto|cpu|cuda"),
) -> None:
    """Ingest a video, run AI mocap, write skeleton + export files."""
    setup_logging()
    settings = load_settings(preset=preset, device=device)
    orch = JobOrchestrator(settings=settings, out_dir=out)
    result = orch.run(video)
    console.print(f"[bold green]done[/] frames={result.frame_count} fps={result.fps:.2f} out={out}")


@app.command()
def inspect(video: Path = typer.Argument(..., exists=True, dir_okay=False)) -> None:
    """Probe container/codec/frame metadata without running the model."""
    from mocap.ingest.probe import probe_video

    info = probe_video(video)
    console.print(info.as_table())


if __name__ == "__main__":
    app()