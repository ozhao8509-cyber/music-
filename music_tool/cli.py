"""从 inbox/<歌名> 跑一次状态机。"""

from __future__ import annotations

import sys
from pathlib import Path

from music_tool.state_machine import run_song


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        print("用法: python -m music_tool inbox/<歌名>", file=sys.stderr)
        return 2
    song_dir = Path(args[0])
    if not song_dir.is_dir():
        print(f"找不到歌曲目录: {song_dir}", file=sys.stderr)
        return 2
    action = run_song(song_dir)
    print(action)
    return 0
