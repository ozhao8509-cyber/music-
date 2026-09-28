"""按动作把分轨和 MIDI 落到 done 或 review。"""

from __future__ import annotations

import json
import shutil
from pathlib import Path


def run(ctx: dict) -> None:
    action = ctx.get("action") or "handoff"
    if action not in {"continue", "audio_only", "handoff"}:
        ctx["errors"].append("bad_action")
        action = "handoff"
        ctx["action"] = action

    destination_root = ctx["root"] / ("review" if action == "handoff" else "done")
    destination = destination_root / ctx["song"]
    destination.mkdir(parents=True, exist_ok=True)
    audio_dir = destination / "audio"
    midi_dir = destination / "midi"
    audio_dir.mkdir(exist_ok=True)
    midi_dir.mkdir(exist_ok=True)

    keep_midi = action == "continue"
    for name, stem in ctx["stems"].items():
        if not stem["present"] or not stem["source"]:
            continue
        source = Path(stem["source"])
        shutil.copy2(source, audio_dir / source.name)
        midi_source = ctx["root"] / "logs" / ctx["song"] / "midi" / f"{name}.mid"
        if keep_midi and stem.get("disposition") != "audio_only" and stem.get("midi_written") and midi_source.exists():
            shutil.copy2(midi_source, midi_dir / f"{name}.mid")

    job = {
        "song": ctx["song"],
        "action": action,
        "steps": ["ingest", "transcribe", "score", "duty", "finish"],
        "errors": list(ctx["errors"]),
        "stems": ctx["stems"],
    }
    (destination / "job.json").write_text(
        json.dumps(job, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    ctx["log"].write(f"finish action {action} path {destination}")
