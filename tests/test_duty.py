import json
import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch

from music_tool.state_machine import run_song


def _tone(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "w") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(8000)
        handle.writeframes(b"\x00\x00" * 800)


class DutyOfficerTest(unittest.TestCase):
    def test_missing_stems_go_to_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            song = root / "inbox" / "empty"
            song.mkdir(parents=True)
            action = run_song(song, root)
            self.assertEqual(action, "handoff")
            self.assertTrue((root / "review" / "empty" / "job.json").exists())
            self.assertFalse((root / "done" / "empty" / "job.json").exists())

    def test_guitar_only_keeps_audio(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            song = root / "inbox" / "gtr"
            _tone(song / "guitar.wav")
            action = run_song(song, root)
            job = json.loads((root / "done" / "gtr" / "job.json").read_text(encoding="utf-8"))
            self.assertEqual(action, "audio_only")
            self.assertEqual(job["action"], "audio_only")
            self.assertEqual(list((root / "done" / "gtr" / "midi").glob("*.mid")), [])


if __name__ == "__main__":
    unittest.main()
