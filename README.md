# open-source-transcriptor

Local YouTube transcription CLI. Other agents can run it and get a markdown file back. The chat model does not have to listen to the video, fetch captions by hand, or burn tokens rewriting speech.

Flow:

1. Pull video metadata with `yt-dlp`
2. Use official YouTube captions if they exist
3. Fall back to local [faster-whisper](https://github.com/SYSTRAN/faster-whisper) when captions are missing
4. Write `*.md`, `*.txt`, or `*.json` to disk

That is the whole product. Run it on your machine. Keep the transcript out of the chat unless someone asks to read it.

## Why this exists

Transcribing a 30 minute video inside an agent session is slow and expensive. YouTube often has no captions. Web fetch on a watch URL returns almost nothing useful.

This CLI does the work locally. The agent only has to run one command and report the file path.

## Requirements

- Python 3.10+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) (installed with the package)
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (installed with the package)
- ffmpeg on `PATH` is recommended. Whisper can still read many audio containers through `av`.

GPU is optional. CPU works. First Whisper run downloads the model into the Hugging Face cache.

## Install

```bash
git clone https://github.com/zlatkomarjanovic/open-source-transcriptor.git
cd open-source-transcriptor
python -m pip install -e .
```

Or without installing the package:

```bash
python -m pip install -r requirements.txt
python -m yt_transcriptor "https://www.youtube.com/watch?v=VIDEO_ID"
```

## CLI

```bash
yt-transcribe "https://www.youtube.com/watch?v=VIDEO_ID"
```

Same thing as a module:

```bash
python -m yt_transcriptor "https://www.youtube.com/watch?v=VIDEO_ID"
```

Video IDs work too:

```bash
yt-transcribe noiFqSAhD7s
```

### Useful flags

| Flag | What it does |
| --- | --- |
| `-o path` | Output file. Default is `<title>-transcript.md` in the current directory |
| `--format md\|txt\|json` | File format. Default `md` |
| `--model small` | Whisper model if captions are missing. `tiny`, `base`, `small`, `medium`, `large-v3` |
| `--language bs` | Force a language code |
| `--device auto\|cpu\|cuda` | Whisper device |
| `--captions-only` | Fail if YouTube has no captions. Never run Whisper |
| `--whisper-only` | Skip captions. Always run Whisper |
| `--keep-audio` | Keep the downloaded audio next to the transcript |
| `--json-summary` | Print a JSON summary to stdout for agents |
| `--print` | Also dump the transcript text to stdout |

### Output

On success, stdout looks like this:

```text
OK file=C:\work\some-video-transcript.md
title=Video title
source=captions
language=en
segments=214
```

`source` is one of `captions`, `auto_captions`, or `whisper`.

Progress goes to stderr. Agents should parse stdout and leave stderr alone.

JSON summary:

```bash
yt-transcribe "URL" --json-summary
```

```json
{
  "ok": true,
  "file": "C:\\work\\some-video-transcript.md",
  "title": "Video title",
  "channel": "Channel name",
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "video_id": "VIDEO_ID",
  "duration": 1906,
  "language": "en",
  "source": "captions",
  "segments": 214
}
```

### Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Transcript written |
| `1` | Runtime error |
| `2` | Bad URL or bad flags |
| `3` | `--captions-only` and the video has no captions |

## Markdown shape

```markdown
# Video title

- **Channel:** ...
- **URL:** ...
- **Video ID:** `...`
- **Duration:** 31:46
- **Published:** 2026-09-25
- **Language:** bs
- **Source:** ...

## Full transcript

**[00:00]** First paragraph.

**[00:19]** Next paragraph.

## Plain text

Full text without timestamps.
```

## Agent usage

Read [AGENTS.md](./AGENTS.md) before you transcribe anything.

Short version:

1. Do not transcribe in the chat.
2. Do not scrape the YouTube watch page for a transcript.
3. Run `yt-transcribe "<url>" --json-summary`.
4. Tell the user the output file path.
5. Do not paste the full transcript unless they ask.

Copy-paste prompt: [DEMO_PROMPT.md](./DEMO_PROMPT.md)

Cursor skill: [skills/yt-transcribe/SKILL.md](./skills/yt-transcribe/SKILL.md)

## Examples

Captions only, no Whisper:

```bash
yt-transcribe "https://www.youtube.com/watch?v=VIDEO_ID" --captions-only -o talk.md
```

Force local speech-to-text:

```bash
yt-transcribe "https://www.youtube.com/watch?v=VIDEO_ID" --whisper-only --model small --language bs
```

JSON file for another tool:

```bash
yt-transcribe "https://www.youtube.com/watch?v=VIDEO_ID" --format json -o talk.json
```

## Notes

- Public videos only. Private and members-only videos will fail.
- Auto captions and Whisper both make mistakes, especially on dialect, overlap, and noisy rooms.
- Larger Whisper models are slower and usually cleaner. `small` is the default because it is a sane local default.
- The first Whisper model download can take a few minutes. Later runs reuse the cache.

## License

MIT. See [LICENSE](./LICENSE).
