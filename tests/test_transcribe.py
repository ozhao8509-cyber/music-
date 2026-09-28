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


class TranscribeDispatchTest(unittest.TestCase):
    def test_guitar_skips_model_and_piano_calls_it(self) -> None:
        calls: list[str] = []

        def fake_transcribe(audio_path: Path, midi_path: Path) -> float:
            calls.append(audio_path.name)
            midi_path.parent.mkdir(parents=True, exist_ok=True)
            midi_path.write_bytes(b"MThd")
            return 0.8

        with tempfile.TemporaryDirectory() as tmp, patch(
            "music_tool.models.transcribe_file", fake_transcribe
        ):
            root = Path(tmp)
            song = root / "inbox" / "band"
            _tone(song / "piano.wav")
            _tone(song / "guitar.wav")
            run_song(song, root)
            job = json.loads((root / "done" / "band" / "job.json").read_text(encoding="utf-8"))
            piano_midi = root / "done" / "band" / "midi" / "piano.mid"
            guitar_midi = root / "done" / "band" / "midi" / "guitar.mid"
            self.assertEqual(calls, ["piano.wav"])
            self.assertEqual(job["stems"]["guitar"]["disposition"], "audio_only")
            self.assertTrue(piano_midi.exists())
            self.assertFalse(guitar_midi.exists())


if __name__ == "__main__":
    unittest.main()
