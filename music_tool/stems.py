"""轨道名。状态机只认这些名字，缺了就记日志，不发明音轨。"""

from __future__ import annotations

AUDIO_EXTENSIONS = {".wav", ".mp3", ".flac", ".aiff", ".aif", ".m4a", ".aac", ".wma"}

STEM_ORDER = ("vocals", "drums", "bass", "guitar", "piano", "other")

# 这一版不跑重模型的轨。分数阶段会把它们标成低置信度。
LITE_STEMS = frozenset({"guitar", "other"})

ALIASES = {
    "vocals": ("vocals", "vocal", "voice", "vox", "人声"),
    "drums": ("drums", "drum", "鼓"),
    "bass": ("bass", "贝斯"),
    "guitar": ("guitar", "吉他"),
    "piano": ("piano", "钢琴"),
    "other": ("other", "others", "其他"),
}


def match_stem(filename: str) -> str | None:
    stem = filename.rsplit(".", 1)[0].lower().replace("_", " ").replace("-", " ")
    for name in STEM_ORDER:
        for alias in ALIASES[name]:
            if alias.lower() in stem:
                return name
    return None
