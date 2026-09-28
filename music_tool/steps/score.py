"""把转录结果写成每轨置信度。不决定整首歌的动作。"""

from __future__ import annotations

from music_tool.stems import LITE_STEMS, STEM_ORDER

# 吉他和其他轨固定低于任何合理阈值，所以值班员只会留下音频。
LITE_CONFIDENCE = 0.2


def run(ctx: dict) -> None:
    for name in STEM_ORDER:
        stem = ctx["stems"][name]
        if not stem["present"]:
            continue
        result = ctx["transcriptions"][name]
        stem["midi_written"] = bool(result["midi_written"])
        stem["error"] = result["error"]
        if result["error"]:
            stem["confidence"] = 0.0
            ctx["errors"].append(f"transcribe_failed:{name}")
            ctx["log"].write(f"score error {name}")
            continue
        if name in LITE_STEMS or result["skipped"]:
            stem["confidence"] = LITE_CONFIDENCE
            stem["disposition"] = "audio_only"
            ctx["log"].write(f"score {name} confidence {LITE_CONFIDENCE} audio_only")
            continue
        stem["confidence"] = result["confidence"]
        ctx["log"].write(f"score {name} confidence {stem['confidence']}")
