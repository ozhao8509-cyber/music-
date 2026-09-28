"""确认转录模型已经在本机，并把位置记到缓存。不把权重复制进仓库。"""

from __future__ import annotations

import sys
from pathlib import Path

from music_tool.models import MODEL_NAME, model_path


def cache_file() -> Path:
    return Path.home() / ".cache" / "music-tool" / "models" / f"{MODEL_NAME}.path"


def ensure_model() -> Path:
    path = model_path()
    if not path.exists():
        raise FileNotFoundError(f"找不到模型文件: {path}")
    destination = cache_file()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(str(path) + "\n", encoding="utf-8")
    return path


def main() -> int:
    try:
        path = ensure_model()
    except Exception as exc:  # 缺包或缺文件都要让朋友看到同一句安装提示
        print(f"模型还没准备好: {exc}", file=sys.stderr)
        print("先执行: pip install -r requirements.txt", file=sys.stderr)
        return 1
    print(f"{MODEL_NAME} {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
