"""调用值班员。模型答偏了就改用规则，五步仍然走完。"""

from __future__ import annotations

from music_tool.duty_officer import choose


def run(ctx: dict) -> None:
    ctx["action"] = choose(ctx)
    ctx["log"].write(f"duty action {ctx['action']}")
