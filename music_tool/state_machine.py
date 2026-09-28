"""五步状态机。顺序写死，调用方不能改。"""

from __future__ import annotations

from pathlib import Path

from music_tool.log import StepLog
from music_tool.steps import duty, finish, ingest, score, transcribe

STEPS = (
    ("ingest", ingest.run),
    ("transcribe", transcribe.run),
    ("score", score.run),
    ("duty", duty.run),
    ("finish", finish.run),
)


def run_song(song_dir: Path, root: Path | None = None) -> str:
    song_dir = song_dir.resolve()
    if root is None:
        root = song_dir.parent.parent if song_dir.parent.name == "inbox" else Path.cwd()
    root = root.resolve()
    song = song_dir.name
    done_job = root / "done" / song / "job.json"
    log = StepLog(root / "logs" / f"{song}.log")
    if done_job.exists():
        log.write("skip already_done")
        return "skip"

    ctx = {
        "root": root,
        "song": song,
        "song_dir": song_dir,
        "log": log,
        "errors": [],
        "stems": {},
        "transcriptions": {},
        "action": None,
    }
    for number, (name, step) in enumerate(STEPS, start=1):
        log.step(number, name, "start")
        step(ctx)
        log.step(number, name, "end")
    return ctx["action"] or "handoff"
