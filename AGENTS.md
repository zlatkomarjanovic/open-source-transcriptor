# Agent instructions

This repo is a local CLI. You run it. You do not reimplement it in the chat.

## When to use it

Use `yt-transcribe` when the user wants a YouTube transcript, captions, subtitles, or a markdown/text dump of a video.

Also use it when you are about to:

- open a YouTube watch page and hunt for captions
- ask the model to "listen" to a video
- download audio and invent your own Whisper wrapper
- paste a long transcript into the conversation just to store it

## Hard rules

1. Never transcribe speech inside the LLM. That wastes usage and is worse than this CLI.
2. Never use browser/WebFetch on `youtube.com/watch` as the transcript source. The watch page does not give you the captions.
3. Never write a one-off Python script if `yt-transcribe` is already installed.
4. Never paste the full transcript into chat unless the user asked to see it.
5. Always write the file locally, then report the path.

## Install if missing

From the repo root:

```bash
python -m pip install -e .
```

Check it:

```bash
yt-transcribe --help
python -m yt_transcriptor --help
```

If the command is not on `PATH`, use `python -m yt_transcriptor`.

## Command to run

Preferred:

```bash
yt-transcribe "<youtube-url-or-id>" --json-summary
```

If the user named an output file:

```bash
yt-transcribe "<youtube-url-or-id>" -o "<path>" --json-summary
```

If they asked for a language:

```bash
yt-transcribe "<url>" --language bs --json-summary
```

If they asked for captions only, no speech-to-text:

```bash
yt-transcribe "<url>" --captions-only --json-summary
```

If they want Whisper even when captions exist:

```bash
yt-transcribe "<url>" --whisper-only --model small --json-summary
```

Do not pass `--print` unless the user wants the text in the terminal.

## How to read the result

Parse stdout JSON when `--json-summary` is set.

You need these fields:

- `ok`
- `file`
- `title`
- `source` (`captions`, `auto_captions`, or `whisper`)
- `language`
- `segments`

Stderr is progress. Ignore it unless the command failed.

## What to tell the user

Keep it short:

- file path
- video title
- source (`captions` vs Whisper)
- language
- one sentence if Whisper was used because YouTube had no captions

Do not dump the markdown into the chat.

If they then ask for a summary, read the file and summarize. Do not rerun transcription.

## Failures

| Exit code | What you do |
| --- | --- |
| `0` | Report the file. Stop. |
| `2` | The URL is bad. Ask for a real YouTube URL or 11-character ID. |
| `3` | No captions and `--captions-only` was set. Tell the user and offer a Whisper run. |
| `1` | Read stderr. Common causes: private video, missing network, missing model download, missing ffmpeg. |

Do not retry the same failed command in a loop.

## Do not do this

```text
Bad: scrape https://youtubegpt.ai or similar sites
Bad: write a new Whisper script in /tmp
Bad: download the mp3 and then ask the chat model to transcribe it
Bad: return a 2,000 line transcript in the assistant message
```

```text
Good: yt-transcribe "URL" --json-summary
Good: "Saved to C:\work\title-transcript.md. Source: whisper (no YouTube captions)."
```
