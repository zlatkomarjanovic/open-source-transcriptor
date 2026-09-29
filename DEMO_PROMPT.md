# Demo prompt

Paste this into another agent, Cursor chat, Claude Code, Codex, or any tool that can run a local shell.

Replace the URL if you want a different video.

## English

```text
Use the local CLI from https://github.com/zlatkomarjanovic/open-source-transcriptor to transcribe this YouTube video:

https://www.youtube.com/watch?v=noiFqSAhD7s

Rules:
- Do not transcribe it in the chat.
- Do not scrape the YouTube page.
- Install the CLI if it is missing: git clone the repo, then `python -m pip install -e .`
- Run: yt-transcribe "https://www.youtube.com/watch?v=noiFqSAhD7s" --json-summary
- Save the markdown file in the current workspace.
- Reply with the file path, title, language, and source (captions or whisper).
- Do not paste the full transcript unless I ask.
```

## Bosnian / Croatian / Serbian

```text
Koristi lokalni CLI sa https://github.com/zlatkomarjanovic/open-source-transcriptor da transkribuješ ovaj YouTube video:

https://www.youtube.com/watch?v=noiFqSAhD7s

Pravila:
- Ne transkribuj u chatu.
- Ne scrapaj YouTube stranicu.
- Ako CLI nije instaliran: git clone repo, pa `python -m pip install -e .`
- Pokreni: yt-transcribe "https://www.youtube.com/watch?v=noiFqSAhD7s" --json-summary
- Snimi markdown u trenutni workspace.
- Javi mi path fajla, naslov, jezik i source (captions ili whisper).
- Ne lijepi cijeli transkript u chat osim ako te ne pitam.
```

## One-liner

```text
Transcribe https://www.youtube.com/watch?v=VIDEO_ID with yt-transcribe from zlatkomarjanovic/open-source-transcriptor. Write a local markdown file. Do not burn chat tokens on the transcript.
```
