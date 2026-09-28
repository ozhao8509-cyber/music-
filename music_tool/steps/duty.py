"""值班员的挂接点。feat 分支固定继续，决策在 duty 分支替换。"""

from __future__ import annotations


def run(ctx: dict) -> None:
    ctx["action"] = "continue"
    ctx["log"].write("duty action continue")
