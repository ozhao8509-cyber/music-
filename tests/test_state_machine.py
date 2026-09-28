import json
import tempfile
import unittest
import wave
from pathlib import Path

from music_tool.state_machine import STEPS, run_song


def _tone(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "w") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(8000)
        handle.writeframes(b"\x00\x00" * 800)


class StateMachineTest(unittest.TestCase):
    def test_steps_are_fixed(self) -> None:
        self.assertEqual(
            [name for name, _ in STEPS],
            ["ingest", "transcribe", "score", "duty", "finish"],
        )

    def test_log_order_and_no_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            song = root / "inbox" / "demo"
            _tone(song / "vocals.wav")
            _tone(song / "drums.wav")
            _tone(song / "unknown-room.wav")

            action = run_song(song, root)
            self.assertEqual(action, "continue")
            log = (root / "logs" / "demo.log").read_text(encoding="utf-8").splitlines()
            step_lines = [line for line in log if line.startswith("step ")]
            expected = []
            for number, name in enumerate([name for name, _ in STEPS], start=1):
                expected.extend([f"step {number} {name} start", f"step {number} {name} end"])
            self.assertEqual(step_lines, expected)

            job_path = root / "done" / "demo" / "job.json"
            first = job_path.read_text(encoding="utf-8")
            job = json.loads(first)
            self.assertEqual(job["action"], "continue")
            self.assertTrue(job["stems"]["vocals"]["present"])
            self.assertFalse(job["stems"]["piano"]["present"])
            self.assertIn("ingest note unmatched unknown-room.wav", log)

            action = run_song(song, root)
            self.assertEqual(action, "skip")
            self.assertEqual(job_path.read_text(encoding="utf-8"), first)
            rerun = (root / "logs" / "demo.log").read_text(encoding="utf-8").splitlines()
            self.assertEqual(rerun[-1], "skip already_done")
            self.assertEqual(rerun.count("step 1 ingest start"), 1)


if __name__ == "__main__":
    unittest.main()
