"""值班员只回答 continue、audio_only、handoff。"""

from __future__ import annotations

ACTIONS = ("continue", "audio_only", "handoff")
THRESHOLD = 0.5


def mark_stems(ctx: dict) -> None:
    for stem in ctx["stems"].values():
        if not stem["present"]:
            continue
        confidence = stem["confidence"]
        if confidence is None or confidence < THRESHOLD:
            stem["disposition"] = "audio_only"
        else:
            stem["disposition"] = "midi"


def decide_rules(ctx: dict) -> str:
    mark_stems(ctx)
    present = [stem for stem in ctx["stems"].values() if stem["present"]]
    if not present or ctx["errors"]:
        return "handoff"
    if all(stem["disposition"] == "audio_only" for stem in present):
        return "audio_only"
    return "continue"
