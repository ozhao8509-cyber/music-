"""转录这一步的位置。模型调用在 model 分支里补上。"""

from __future__ import annotations

from music_tool.stems import LITE_STEMS, STEM_ORDER


def run(ctx: dict) -> None:
    ctx["transcriptions"] = {}
    for name in STEM_ORDER:
        stem = ctx["stems"][name]
        if not stem["present"]:
            ctx["transcriptions"][name] = {
                "midi_written": False,
                "confidence": None,
                "error": None,
                "skipped": False,
            }
            continue
        if name in LITE_STEMS:
            ctx["log"].write(f"transcribe skip {name}")
            ctx["transcriptions"][name] = {
                "midi_written": False,
                "confidence": None,
                "error": None,
                "skipped": True,
            }
            continue
        ctx["transcriptions"][name] = transcribe_stem(ctx, name)


def transcribe_stem(ctx: dict, name: str) -> dict:
    from pathlib import Path

    from music_tool.models import transcribe_file

    midi_path = ctx["root"] / "logs" / ctx["song"] / "midi" / f"{name}.mid"
    try:
        confidence = transcribe_file(Path(ctx["stems"][name]["source"]), midi_path)
    except Exception as exc:
        ctx["log"].write(f"transcribe error {name} {exc}")
        return {
            "midi_written": False,
            "confidence": None,
            "error": str(exc),
            "skipped": False,
        }
    ctx["log"].write(f"transcribe wrote {name}")
    return {
        "midi_written": True,
        "confidence": confidence,
        "error": None,
        "skipped": False,
    }
