from harness.jsonutil import parse_json_object


def test_parse_raw_object() -> None:
    assert parse_json_object('{"answer": "ok"}') == {"answer": "ok"}


def test_parse_fenced_json() -> None:
    text = "here you go\n```json\n{\"album_id\": \"abc\"}\n```\n"
    assert parse_json_object(text)["album_id"] == "abc"


def test_parse_embedded_object() -> None:
    assert parse_json_object("Sure. {\"used_tool\": true}") == {"used_tool": True}
