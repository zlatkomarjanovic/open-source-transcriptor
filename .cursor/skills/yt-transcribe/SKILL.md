---
name: yt-transcribe
description: Transcribe YouTube videos locally with the yt-transcribe CLI. Use when the user wants a YouTube transcript, captions, subtitles, or a markdown dump of a video. Never transcribe in chat.
---

# yt-transcribe

Local CLI. Captions first. Whisper fallback. File on disk. Chat stays small.

Repo: https://github.com/zlatkomarjanovic/open-source-transcriptor

## Do this

```bash
yt-transcribe "<youtube-url-or-id>" --json-summary
```

If the command is missing:

```bash
python -m pip install -e .
python -m yt_transcriptor "<url>" --json-summary
```

## Reply

Report `file`, `title`, `source`, and `language` from the JSON summary.

Do not paste the transcript unless the user asks.

## Do not do this

- Transcribe inside the LLM
- Fetch `youtube.com/watch` and hope captions are in the HTML
- Write a new Whisper script
- Use `--print` unless the user wants terminal output

Full contract: [AGENTS.md](../../../AGENTS.md)
