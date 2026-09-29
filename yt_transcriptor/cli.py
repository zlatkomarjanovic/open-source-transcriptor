from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

from yt_transcriptor import __version__
from yt_transcriptor.render import (
    default_output_path,
    render_json,
    render_markdown,
    render_txt,
    write_output,
)
from yt_transcriptor.youtube import download_audio, fetch_captions, fetch_info


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="yt-transcribe",
        description=(
            "Transcribe a YouTube video locally. "
            "Uses official or auto captions when available, otherwise Whisper. "
            "Writes a file so agents do not spend chat tokens on transcription."
        ),
    )
    parser.add_argument("url", help="YouTube URL or 11-character video ID")
    parser.add_argument(
        "-o",
        "--output",
        help="Output file path. Default: <title>-transcript.md in the current directory",
    )
    parser.add_argument(
        "--format",
        choices=("md", "txt", "json"),
        default="md",
        help="Output format (default: md)",
    )
    parser.add_argument(
        "--model",
        default="small",
        help="faster-whisper model when captions are missing (default: small)",
    )
    parser.add_argument(
        "--language",
        help="Force language code, e.g. en, bs, hr, sr, de",
    )
    parser.add_argument(
        "--device",
        choices=("auto", "cpu", "cuda"),
        default="auto",
        help="Whisper device (default: auto)",
    )
    parser.add_argument(
        "--captions-only",
        action="store_true",
        help="Fail if YouTube has no captions. Never run Whisper.",
    )
    parser.add_argument(
        "--whisper-only",
        action="store_true",
        help="Skip YouTube captions and always run Whisper.",
    )
    parser.add_argument(
        "--keep-audio",
        action="store_true",
        help="Keep the downloaded audio file next to the transcript",
    )
    parser.add_argument(
        "--json-summary",
        action="store_true",
        help="Print a machine-readable JSON summary to stdout",
    )
    parser.add_argument(
        "--print",
        dest="print_text",
        action="store_true",
        help="Also print the transcript text to stdout",
    )
    parser.add_argument("--version", action="version", version=f"yt-transcribe {__version__}")
    return parser


def _log(message: str) -> None:
    print(message, file=sys.stderr, flush=True)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.captions_only and args.whisper_only:
        _log("Use either --captions-only or --whisper-only, not both.")
        return 2

    try:
        _log("Fetching video metadata...")
        info = fetch_info(args.url)
        _log(f"Title: {info.title}")
        _log(f"Channel: {info.channel}")

        segments = []
        source = "whisper"
        language = args.language or "unknown"
        confidence = None

        if not args.whisper_only:
            _log("Checking YouTube captions...")
            caption_result = fetch_captions(info, language=args.language)
            if caption_result:
                segments, language, source = caption_result
                _log(f"Using {source} ({language}, {len(segments)} segments).")

        if not segments:
            if args.captions_only:
                _log("No YouTube captions available.")
                return 3
            _log(f"No captions. Transcribing with Whisper ({args.model})...")
            from yt_transcriptor.whisper_engine import transcribe_audio

            workdir = Path(args.output).parent if args.output else Path.cwd()
            with tempfile.TemporaryDirectory(prefix="yt-transcriptor-") as tmp:
                audio_path = download_audio(info, Path(tmp))
                if args.keep_audio:
                    kept = workdir / audio_path.name
                    kept.write_bytes(audio_path.read_bytes())
                    _log(f"Audio saved: {kept}")
                segments, language, confidence = transcribe_audio(
                    audio_path,
                    model_name=args.model,
                    language=args.language,
                    device=args.device,
                )
            source = "whisper"

        if not segments:
            _log("Transcription produced no text.")
            return 1

        dest_dir = Path(args.output).parent if args.output else Path.cwd()
        output_path = (
            Path(args.output) if args.output else default_output_path(info, args.format, dest_dir)
        )
        if args.output and output_path.suffix.lower() not in {".md", ".txt", ".json"}:
            output_path = output_path.with_suffix(
                { "md": ".md", "txt": ".txt", "json": ".json" }[args.format]
            )

        if args.format == "txt":
            content = render_txt(info, segments)
        elif args.format == "json":
            content = render_json(
                info,
                segments,
                source=source,
                language=language,
                language_confidence=confidence,
                output_file=output_path,
                model_name=args.model if source == "whisper" else None,
            )
        else:
            content = render_markdown(
                info,
                segments,
                source=source,
                language=language,
                language_confidence=confidence,
                model_name=args.model if source == "whisper" else None,
            )

        write_output(output_path, content)

        summary = {
            "ok": True,
            "file": str(output_path.resolve()),
            "title": info.title,
            "channel": info.channel,
            "url": info.url,
            "video_id": info.id,
            "duration": info.duration,
            "language": language,
            "source": source,
            "segments": len(segments),
        }

        if args.json_summary:
            print(json.dumps(summary, ensure_ascii=False))
        else:
            print(f"OK file={summary['file']}")
            print(f"title={info.title}")
            print(f"source={source}")
            print(f"language={language}")
            print(f"segments={len(segments)}")

        if args.print_text:
            print()
            print(" ".join(item.text for item in segments))

        return 0
    except ValueError as exc:
        _log(str(exc))
        return 2
    except Exception as exc:
        _log(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
