"""按置信度选择三个动作之一。"""

from __future__ import annotations

from music_tool.duty_officer import decide_rules


def run(ctx: dict) -> None:
    ctx["action"] = decide_rules(ctx)
    ctx["log"].write(f"duty action {ctx['action']}")
