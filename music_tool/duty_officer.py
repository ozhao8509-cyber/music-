"""值班员只回答 continue、audio_only、handoff。"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

ACTIONS = ("continue", "audio_only", "handoff")
THRESHOLD = 0.5


def parse_action(text: str) -> str:
    if not text or not text.strip():
        raise ValueError("empty")
    token = text.strip().split()[0].lower().strip(".,:;")
    if token not in ACTIONS:
        raise ValueError(token)
    return token


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


def complete(model_path: str, log_text: str) -> str:
    prompt = (
        "Reply with exactly one word: continue, audio_only, or handoff.\n\n" + log_text
    )
    try:
        from mlx_lm import generate, load
    except ImportError:
        generate = None
        load = None
    if generate is not None and load is not None:
        model, tokenizer = load(model_path)
        return generate(model, tokenizer, prompt=prompt, max_tokens=8, verbose=False)

    import shutil

    binary = shutil.which("llama-cli") or shutil.which("llama-completion")
    if binary is None:
        raise RuntimeError("neither mlx_lm nor llama-cli is available")
    completed = subprocess.run(
        [binary, "-m", model_path, "-p", prompt, "-n", "8"],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def ask_model(ctx: dict) -> str:
    model_path = os.environ.get("DUTY_MODEL_PATH", "")
    if not model_path:
        raise RuntimeError("DUTY_MODEL_PATH is not set")
    if not Path(model_path).exists():
        raise FileNotFoundError(model_path)
    log_text = Path(ctx["log"].path).read_text(encoding="utf-8")
    return parse_action(complete(model_path, log_text))


def choose(ctx: dict) -> str:
    backend = os.environ.get("DUTY_BACKEND", "rules")
    if backend == "model":
        try:
            action = ask_model(ctx)
        except Exception as exc:
            ctx["log"].write(f"duty model fallback {exc}")
        else:
            mark_stems(ctx)
            ctx["log"].write(f"duty backend model action {action}")
            return action
    action = decide_rules(ctx)
    ctx["log"].write(f"duty backend rules action {action}")
    return action
