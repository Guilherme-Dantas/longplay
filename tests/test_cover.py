from apps.workout_album.policy import AlbumPick
from apps.workout_album.runtime import AlbumRecommendation
from apps.workout_album.spotify import SpotifyClient, SpotifyError, cover_url


def test_cover_url_picks_the_sleeve_size() -> None:
    url = cover_url(
        {
            "images": [
                {"url": "https://i.scdn.co/image/large", "width": 640, "height": 640},
                {"url": "https://i.scdn.co/image/mid", "width": 300, "height": 300},
                {"url": "https://i.scdn.co/image/tiny", "width": 64, "height": 64},
            ]
        }
    )
    assert url == "https://i.scdn.co/image/large"


def test_cover_url_rejects_a_foreign_host() -> None:
    assert cover_url({"images": [{"url": "https://evil.example/a.jpg", "width": 640}]}) is None
    assert cover_url({"images": [{"url": "http://i.scdn.co/image/plain", "width": 640}]}) is None


def test_cover_for_reuses_the_search_image_without_another_get() -> None:
    client = SpotifyClient(client_id="id", client_secret="secret")
    client._remember_cover(
        {
            "id": "abc",
            "images": [{"url": "https://i.scdn.co/image/abc", "width": 640, "height": 640}],
        }
    )

    def fail_get(path: str, params: dict | None = None) -> dict:
        raise AssertionError(path)

    client._get = fail_get  # type: ignore[method-assign]
    assert client.cover_for("abc") == "https://i.scdn.co/image/abc"


def test_missing_cover_stays_empty_when_spotify_has_no_image() -> None:
    client = SpotifyClient(client_id="id", client_secret="secret")

    def empty_album(path: str, params: dict | None = None) -> dict:
        return {"id": "abc", "images": []}

    client._get = empty_album  # type: ignore[method-assign]
    pick = AlbumPick(
        album_id="abc",
        name="Dummy",
        artists=["Portishead"],
        duration_ms=2_700_000,
        duration_minutes=45.0,
        reason="Fits the clock.",
        spotify_url="https://open.spotify.com/album/abc",
    )
    recommendation = AlbumRecommendation(**pick.model_dump(), image_url=client.cover_for(pick.album_id))
    assert recommendation.image_url is None


def test_cover_lookup_failure_does_not_invent_a_url() -> None:
    client = SpotifyClient(client_id="id", client_secret="secret")

    def down(path: str, params: dict | None = None) -> dict:
        raise SpotifyError("down")

    client._get = down  # type: ignore[method-assign]
    assert client.cover_for("missing") is None
