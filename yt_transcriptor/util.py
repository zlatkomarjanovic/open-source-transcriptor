from __future__ import annotations

import re
from datetime import datetime
from urllib.parse import parse_qs, urlparse


YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtu.be",
    "www.youtu.be",
}


def extract_video_id(url_or_id: str) -> str:
    raw = url_or_id.strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", raw):
        return raw

    parsed = urlparse(raw)
    host = (parsed.hostname or "").lower()
    if host not in YOUTUBE_HOSTS:
        raise ValueError(f"Not a YouTube URL: {url_or_id}")

    if host.endswith("youtu.be"):
        video_id = parsed.path.strip("/").split("/")[0]
    elif parsed.path.startswith("/shorts/"):
        video_id = parsed.path.split("/")[2] if len(parsed.path.split("/")) > 2 else ""
    elif parsed.path.startswith("/embed/"):
        video_id = parsed.path.split("/")[2] if len(parsed.path.split("/")) > 2 else ""
    elif parsed.path.startswith("/live/"):
        video_id = parsed.path.split("/")[2] if len(parsed.path.split("/")) > 2 else ""
    else:
        video_id = parse_qs(parsed.query).get("v", [""])[0]

    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        raise ValueError(f"Could not extract a YouTube video ID from: {url_or_id}")
    return video_id


def canonical_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def format_duration(seconds: int | float | None) -> str:
    total = int(seconds or 0)
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def format_timestamp(seconds: float) -> str:
    total = max(0, int(seconds))
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def parse_timestamp(stamp: str) -> float:
    parts = stamp.split(":")
    values = [float(p) for p in parts]
    if len(values) == 3:
        return values[0] * 3600 + values[1] * 60 + values[2]
    if len(values) == 2:
        return values[0] * 60 + values[1]
    return values[0]


def format_upload_date(raw: str | None) -> str:
    if not raw or len(raw) != 8 or not raw.isdigit():
        return raw or "Unknown"
    return datetime.strptime(raw, "%Y%m%d").strftime("%Y-%m-%d")


def slugify(title: str, fallback: str = "transcript") -> str:
    pieces: list[str] = []
    for char in title:
        if char.isalnum():
            pieces.append(char)
        elif char in " -_:." and (not pieces or pieces[-1] != "-"):
            pieces.append("-")
    slug = "".join(pieces).strip("-")
    return slug[:80] or fallback


def pick_device(requested: str) -> tuple[str, str]:
    if requested == "cpu":
        return "cpu", "int8"
    if requested == "cuda":
        return "cuda", "float16"

    try:
        import ctranslate2

        if ctranslate2.get_cuda_device_count() > 0:
            return "cuda", "float16"
    except Exception:
        pass
    return "cpu", "int8"
