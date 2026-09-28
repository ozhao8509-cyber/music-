"""追加步骤日志。朋友用它核对 1 到 5 没有跳步。"""

from __future__ import annotations

from pathlib import Path


class StepLog:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, line: str) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")

    def step(self, number: int, name: str, phase: str) -> None:
        self.write(f"step {number} {name} {phase}")
