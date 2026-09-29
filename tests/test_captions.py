from yt_transcriptor.captions import parse_caption_text, parse_captions, parse_json3
from yt_transcriptor.render import group_paragraphs


VTT = """WEBVTT

00:00:00.000 --> 00:00:03.000
Hello world

00:00:03.000 --> 00:00:06.120
Second line
"""


JSON3 = """{
  "events": [
    {"tStartMs": 0, "segs": [{"utf8": "Hello "}, {"utf8": "world"}]},
    {"tStartMs": 3120, "segs": [{"utf8": "Second line"}]}
  ]
}
"""


def test_parse_vtt():
    segments = parse_caption_text(VTT)
    assert segments[0].text == "Hello world"
    assert segments[1].start == 3.0


def test_parse_json3():
    segments = parse_json3(JSON3)
    assert [item.text for item in segments] == ["Hello world", "Second line"]
    assert segments[1].start == 3.12


def test_parse_captions_dispatches_json():
    segments = parse_captions(JSON3, ext="json3")
    assert segments[0].text == "Hello world"


def test_group_paragraphs_keeps_close_lines_together():
    from yt_transcriptor.captions import Segment

    grouped = group_paragraphs(
        [
            Segment(0, "One."),
            Segment(1.2, "Two."),
            Segment(8.0, "Later."),
        ]
    )
    assert grouped[0].text == "One. Two."
    assert grouped[1].text == "Later."
