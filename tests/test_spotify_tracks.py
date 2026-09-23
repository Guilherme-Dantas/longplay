from apps.workout_album.spotify import SpotifyClient, SpotifyError


def test_track_pages_advance_by_offset() -> None:
    client = SpotifyClient(client_id="id", client_secret="secret")
    calls: list[dict] = []

    def fake_get(path: str, params: dict | None = None) -> dict:
        calls.append(dict(params or {}))
        offset = int((params or {}).get("offset") or 0)
        if offset == 0:
            items = [{"id": "a", "name": "A", "duration_ms": 1000, "track_number": 1}] * 50
            return {"items": items, "total": 60}
        items = [{"id": "b", "name": "B", "duration_ms": 2000, "track_number": 51}] * 10
        return {"items": items, "total": 60}

    client._get = fake_get  # type: ignore[method-assign]
    result = client.get_album_tracks("album")
    assert result["track_count"] == 60
    assert [call["offset"] for call in calls] == [0, 50]


def test_track_pages_stop_when_spotify_repeats_forever() -> None:
    client = SpotifyClient(client_id="id", client_secret="secret")

    def fake_get(path: str, params: dict | None = None) -> dict:
        items = [{"id": "a", "name": "A", "duration_ms": 1000, "track_number": 1}] * 50
        return {"items": items, "total": 10_000}

    client._get = fake_get  # type: ignore[method-assign]
    try:
        client.get_album_tracks("album")
    except SpotifyError as exc:
        assert "did not end" in str(exc)
    else:
        raise AssertionError("expected the page cap to fail the album")
