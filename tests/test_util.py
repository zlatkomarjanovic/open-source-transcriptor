from yt_transcriptor.util import canonical_url, extract_video_id, format_duration, slugify


def test_extract_watch_url():
    assert extract_video_id("https://www.youtube.com/watch?v=noiFqSAhD7s") == "noiFqSAhD7s"


def test_extract_short_url():
    assert extract_video_id("https://youtu.be/noiFqSAhD7s") == "noiFqSAhD7s"


def test_extract_raw_id():
    assert extract_video_id("noiFqSAhD7s") == "noiFqSAhD7s"


def test_canonical_url():
    assert canonical_url("noiFqSAhD7s") == "https://www.youtube.com/watch?v=noiFqSAhD7s"


def test_format_duration():
    assert format_duration(1906) == "31:46"


def test_slugify():
    assert "RUKIJA" in slugify("RUKIJA IDEMO PO NOVI OSMJEH")
