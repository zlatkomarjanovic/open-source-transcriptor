from __future__ import annotations

import json
from pathlib import Path

from yt_transcriptor.captions import Segment
from yt_transcriptor.util import format_duration, format_timestamp
from yt_transcriptor.youtube import VideoInfo


def group_paragraphs(segments: list[Segment], max_chars: int = 420) -> list[Segment]:
    if not segments:
        return []

    paragraphs: list[Segment] = []
    buffer = [segments[0].text]
    start = segments[0].start
    last = segments[0].start

    for segment in segments[1:]:
        gap = segment.start - last
        last = segment.start
        current = " ".join(buffer)
        ended = buffer[-1].endswith((".", "?", "!"))
        if gap >= 4 or (ended and gap >= 2) or len(current) > max_chars:
            paragraphs.append(Segment(start=start, text=current))
            buffer = [segment.text]
            start = segment.start
        else:
            buffer.append(segment.text)

    if buffer:
        paragraphs.append(Segment(start=start, text=" ".join(buffer)))
    return paragraphs


def render_markdown(
    info: VideoInfo,
    segments: list[Segment],
    *,
    source: str,
    language: str,
    language_confidence: float | None = None,
    model_name: str | None = None,
) -> str:
    language_note = language
    if language_confidence is not None:
        language_note = f"{language} ({language_confidence:.0%} confidence)"

    if source == "captions":
        source_line = "YouTube captions (manual)."
    elif source == "auto_captions":
        source_line = "YouTube auto-generated captions."
    else:
        model = model_name or "small"
        source_line = (
            f"Local Whisper transcription (faster-whisper, `{model}` model). "
            "This video had no usable YouTube captions."
        )

    paragraphs = group_paragraphs(segments)
    timed = "\n\n".join(
        f"**[{format_timestamp(item.start)}]** {item.text}" for item in paragraphs
    )
    plain = " ".join(item.text for item in segments)

    return f"""# {info.title}

- **Channel:** {info.channel}
- **URL:** [{info.url}]({info.url})
- **Video ID:** `{info.id}`
- **Duration:** {format_duration(info.duration)}
- **Published:** {info.upload_date}
- **Language:** {language_note}
- **Source:** {source_line}

## Full transcript

{timed}

## Plain text

{plain}
"""


def render_txt(info: VideoInfo, segments: list[Segment]) -> str:
    header = f"{info.title}\n{info.url}\n\n"
    body = "\n".join(f"[{format_timestamp(item.start)}] {item.text}" for item in segments)
    return header + body + "\n"


def render_json(
    info: VideoInfo,
    segments: list[Segment],
    *,
    source: str,
    language: str,
    language_confidence: float | None,
    output_file: Path,
    model_name: str | None = None,
) -> str:
    payload = {
        "ok": True,
        "file": str(output_file),
        "title": info.title,
        "channel": info.channel,
        "url": info.url,
        "video_id": info.id,
        "duration": info.duration,
        "published": info.upload_date,
        "language": language,
        "language_confidence": language_confidence,
        "source": source,
        "model": model_name,
        "segments": [{"start": item.start, "text": item.text} for item in segments],
        "text": " ".join(item.text for item in segments),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def write_output(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def default_output_path(info: VideoInfo, fmt: str, dest_dir: Path) -> Path:
    from yt_transcriptor.util import slugify

    suffix = {"md": ".md", "txt": ".txt", "json": ".json"}[fmt]
    name = f"{slugify(info.title, fallback=info.id)}-transcript{suffix}"
    return dest_dir / name
