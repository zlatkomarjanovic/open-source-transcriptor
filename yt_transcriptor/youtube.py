from __future__ import annotations

from pathlib import Path

import yt_dlp

from yt_transcriptor.captions import (
    Segment,
    download_text,
    parse_captions,
    pick_caption_track,
)
from yt_transcriptor.util import canonical_url, extract_video_id, format_upload_date


class VideoInfo:
    def __init__(self, raw: dict):
        self.raw = raw
        self.id = raw.get("id") or ""
        self.title = raw.get("title") or "Untitled"
        self.channel = raw.get("channel") or raw.get("uploader") or "Unknown"
        self.duration = int(raw.get("duration") or 0)
        self.upload_date = format_upload_date(raw.get("upload_date"))
        self.url = canonical_url(self.id) if self.id else raw.get("webpage_url", "")


def fetch_info(url_or_id: str) -> VideoInfo:
    video_id = extract_video_id(url_or_id)
    url = canonical_url(video_id)
    options = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(options) as ydl:
        raw = ydl.extract_info(url, download=False)
    if not raw:
        raise RuntimeError("yt-dlp returned no video metadata.")
    return VideoInfo(raw)


def fetch_captions(info: VideoInfo, language: str | None = None) -> tuple[list[Segment], str, str] | None:
    picked = pick_caption_track(info.raw, language=language)
    if not picked:
        return None
    track, lang, source = picked
    content = download_text(track["url"])
    segments = parse_captions(content, ext=track.get("ext"))
    if not segments:
        return None
    return segments, lang, source


def download_audio(info: VideoInfo, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    outtmpl = str(dest_dir / f"{info.id}.%(ext)s")
    options = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "format": "bestaudio/best",
        "outtmpl": outtmpl,
        "overwrites": True,
    }
    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([info.url])

    matches = sorted(dest_dir.glob(f"{info.id}.*"))
    if not matches:
        raise FileNotFoundError(f"Audio download failed for {info.id}")
    return matches[0]
