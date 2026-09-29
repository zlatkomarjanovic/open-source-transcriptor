from __future__ import annotations

from pathlib import Path

from yt_transcriptor.captions import Segment
from yt_transcriptor.util import pick_device


def transcribe_audio(
    audio_path: Path,
    model_name: str = "small",
    language: str | None = None,
    device: str = "auto",
) -> tuple[list[Segment], str, float | None]:
    from faster_whisper import WhisperModel

    resolved_device, compute_type = pick_device(device)
    model = WhisperModel(model_name, device=resolved_device, compute_type=compute_type)
    segments_iter, info = model.transcribe(
        str(audio_path),
        language=language,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 500},
        beam_size=5,
    )

    segments: list[Segment] = []
    for item in segments_iter:
        text = (item.text or "").strip()
        if text:
            segments.append(Segment(start=float(item.start), text=text))

    detected = info.language or language or "unknown"
    probability = getattr(info, "language_probability", None)
    return segments, detected, probability
