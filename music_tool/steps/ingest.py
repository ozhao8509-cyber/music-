"""读取 inbox/<歌名>/ 里的分轨。"""

from __future__ import annotations

from music_tool.stems import AUDIO_EXTENSIONS, STEM_ORDER, match_stem


def run(ctx: dict) -> None:
    song_dir = ctx["song_dir"]
    found = {name: None for name in STEM_ORDER}
    notes: list[str] = []
    if not song_dir.is_dir():
        ctx["errors"].append("missing_song_dir")
        ctx["log"].write("ingest error missing_song_dir")
        ctx["stems"] = _empty_stems()
        return

    for path in sorted(song_dir.iterdir()):
        if not path.is_file() or path.suffix.lower() not in AUDIO_EXTENSIONS:
            continue
        name = match_stem(path.name)
        if name is None:
            notes.append(f"unmatched {path.name}")
            continue
        if found[name] is not None:
            notes.append(f"duplicate {name} {path.name}")
            continue
        found[name] = path

    ctx["stems"] = {
        name: {
            "present": found[name] is not None,
            "source": str(found[name]) if found[name] is not None else None,
            "confidence": None,
            "disposition": None,
            "midi_written": False,
            "error": None,
        }
        for name in STEM_ORDER
    }
    if not any(item["present"] for item in ctx["stems"].values()):
        ctx["errors"].append("no_stems")
        ctx["log"].write("ingest error no_stems")
    for note in notes:
        ctx["log"].write(f"ingest note {note}")


def _empty_stems() -> dict:
    return {
        name: {
            "present": False,
            "source": None,
            "confidence": None,
            "disposition": None,
            "midi_written": False,
            "error": None,
        }
        for name in STEM_ORDER
    }
