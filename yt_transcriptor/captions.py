from __future__ import annotations

import json
import re
from dataclasses import dataclass
from html import unescape
from urllib.request import Request, urlopen


@dataclass
class Segment:
    start: float
    text: str


TIMESTAMP_RE = re.compile(
    r"(?P<start>\d{1,2}:\d{2}(?::\d{2})?[.,]\d{3})\s*-->\s*"
    r"(?P<end>\d{1,2}:\d{2}(?::\d{2})?[.,]\d{3})"
)
TAG_RE = re.compile(r"<[^>]+>")
CUE_SETTINGS_RE = re.compile(
    r"^(align|position|line|size|vertical):", re.IGNORECASE
)


def _to_seconds(raw: str) -> float:
    raw = raw.replace(",", ".")
    parts = raw.split(":")
    numbers = [float(p) for p in parts]
    if len(numbers) == 3:
        return numbers[0] * 3600 + numbers[1] * 60 + numbers[2]
    return numbers[0] * 60 + numbers[1]


def _clean_text(line: str) -> str:
    text = TAG_RE.sub("", unescape(line)).strip()
    return re.sub(r"\s+", " ", text)


def parse_json3(content: str) -> list[Segment]:
    data = json.loads(content)
    segments: list[Segment] = []
    last_text = ""
    for event in data.get("events") or []:
        segs = event.get("segs")
        if not segs:
            continue
        text = _clean_text("".join(part.get("utf8", "") for part in segs))
        if not text or text == last_text:
            continue
        start_ms = event.get("tStartMs") or 0
        segments.append(Segment(start=start_ms / 1000.0, text=text))
        last_text = text
    return segments


def parse_captions(content: str, ext: str | None = None) -> list[Segment]:
    stripped = content.lstrip()
    if ext == "json3" or stripped.startswith("{"):
        try:
            return parse_json3(content)
        except json.JSONDecodeError:
            pass
    return parse_caption_text(content)


def parse_caption_text(content: str) -> list[Segment]:
    segments: list[Segment] = []
    start: float | None = None
    buffer: list[str] = []

    def flush() -> None:
        nonlocal start, buffer
        if start is None:
            buffer = []
            return
        text = _clean_text(" ".join(buffer))
        if text:
            if segments and segments[-1].text == text:
                buffer = []
                start = None
                return
            segments.append(Segment(start=start, text=text))
        buffer = []
        start = None

    for raw_line in content.replace("\r\n", "\n").split("\n"):
        line = raw_line.strip()
        if not line:
            flush()
            continue
        if line.upper().startswith("WEBVTT") or line.upper().startswith("NOTE"):
            continue
        if line.isdigit() and start is None:
            continue
        match = TIMESTAMP_RE.search(line)
        if match:
            flush()
            start = _to_seconds(match.group("start"))
            continue
        if CUE_SETTINGS_RE.match(line):
            continue
        buffer.append(line)

    flush()
    return segments


def download_text(url: str, timeout: int = 30) -> str:
    request = Request(url, headers={"User-Agent": "yt-transcriptor/1.0"})
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


PREFERRED_EXTS = ("vtt", "srv3", "srv1", "json3", "srt")


def pick_caption_track(
    info: dict,
    language: str | None = None,
) -> tuple[dict, str, str] | None:
    """Return (track, language_code, source) or None."""
    buckets = [
        (info.get("subtitles") or {}, "captions"),
        (info.get("automatic_captions") or {}, "auto_captions"),
    ]

    preferred_langs: list[str] = []
    if language:
        preferred_langs.append(language)
        preferred_langs.append(language.split("-")[0])
    preferred_langs.extend(["en", "en-US", "en-GB"])

    def match_lang(store: dict, wanted: str) -> str | None:
        wanted_l = wanted.lower()
        if wanted in store:
            return wanted
        for key in store:
            if key.lower() == wanted_l or key.lower().startswith(wanted_l + "-"):
                return key
        return None

    for store, source in buckets:
        if not store:
            continue
        for wanted in preferred_langs:
            key = match_lang(store, wanted)
            if key:
                track = _best_track(store[key])
                if track:
                    return track, key, source
        for key, tracks in store.items():
            track = _best_track(tracks)
            if track:
                return track, key, source
    return None


def _best_track(tracks: list[dict]) -> dict | None:
    by_ext = {t.get("ext"): t for t in tracks if t.get("url")}
    for ext in PREFERRED_EXTS:
        if ext in by_ext:
            return by_ext[ext]
    return next((t for t in tracks if t.get("url")), None)
