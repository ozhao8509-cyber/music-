"""本机转录。权重来自 basic-pitch 安装包，不放进仓库。"""

from __future__ import annotations

from pathlib import Path

MODEL_NAME = "basic-pitch-icassp-2022"


def model_path() -> Path:
    from basic_pitch import ICASSP_2022_MODEL_PATH

    return Path(ICASSP_2022_MODEL_PATH)


def transcribe_file(audio_path: Path, midi_path: Path) -> float:
    from basic_pitch.inference import predict

    _model_output, midi_data, note_events = predict(
        str(audio_path),
        model_or_model_path=model_path(),
    )
    midi_path.parent.mkdir(parents=True, exist_ok=True)
    midi_data.write(str(midi_path))
    if not note_events:
        return 0.0
    amplitudes = [float(event[3]) for event in note_events]
    return sum(amplitudes) / len(amplitudes)
