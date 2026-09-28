import json
import os
import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch

from music_tool.duty_officer import parse_action
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

    def test_parse_action_rejects_other_words(self) -> None:
        self.assertEqual(parse_action(" audio_only."), "audio_only")
        with self.assertRaises(ValueError):
            parse_action("maybe continue")

    def test_invalid_model_word_falls_back_to_rules(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            model = Path(tmp) / "model.gguf"
            model.write_bytes(b"placeholder")
            root = Path(tmp) / "repo"
            song = root / "inbox" / "song"
            _tone(song / "piano.wav")

            def high(_audio: Path, midi_path: Path) -> float:
                midi_path.parent.mkdir(parents=True, exist_ok=True)
                midi_path.write_bytes(b"MThd")
                return 0.9

            with patch.dict(
                os.environ,
                {"DUTY_BACKEND": "model", "DUTY_MODEL_PATH": str(model)},
            ), patch("music_tool.models.transcribe_file", high), patch(
                "music_tool.duty_officer.complete", return_value="maybe"
            ):
                action = run_song(song, root)
            log = (root / "logs" / "song.log").read_text(encoding="utf-8")
            self.assertEqual(action, "continue")
            self.assertIn("duty model fallback", log)
            self.assertIn("duty action continue", log)


if __name__ == "__main__":
    unittest.main()
