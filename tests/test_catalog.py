from apps.workout_album.catalog import CatalogSearch
from apps.workout_album.musicbrainz import MusicBrainzError


class FakeMB:
    def search_release_groups(self, query: str, limit: int = 5) -> list[dict]:
        return [{"title": "Dummy", "artist": "Portishead", "mbid": "mb-1", "tags": ["trip hop"]}]


class FakeSpotify:
    def search_albums(self, query: str, limit: int = 8) -> dict:
        if "Dummy" in query and "Portishead" in query:
            return {
                "query": query,
                "albums": [
                    {
                        "album_id": "spotify-dummy",
                        "name": "Dummy",
                        "artists": ["Portishead"],
                        "spotify_url": "https://open.spotify.com/album/spotify-dummy",
                    }
                ],
            }
        return {"query": query, "albums": []}


def test_catalog_resolves_mb_hit_on_spotify() -> None:
    catalog = CatalogSearch(spotify=FakeSpotify(), musicbrainz=FakeMB())
    result = catalog.search_albums("trip hop", limit=5)
    assert result["source"] == "musicbrainz+spotify"
    assert result["albums"][0]["album_id"] == "spotify-dummy"
    assert result["albums"][0]["artists"] == ["Portishead"]
    assert "discovery_artist" not in result["albums"][0]


class EmptyMB:
    def search_release_groups(self, query: str, limit: int = 5) -> list[dict]:
        return []


class SpotifyOnly:
    def search_albums(self, query: str, limit: int = 8) -> dict:
        return {
            "query": query,
            "albums": [{"album_id": "plain", "name": "Whatever", "artists": ["X"]}],
        }


def test_catalog_falls_back_to_spotify_when_mb_empty() -> None:
    catalog = CatalogSearch(spotify=SpotifyOnly(), musicbrainz=EmptyMB())
    result = catalog.search_albums("electronic", limit=5)
    assert result["source"] == "spotify"
    assert result["albums"][0]["album_id"] == "plain"


class BoomMB:
    def search_release_groups(self, query: str, limit: int = 5) -> list[dict]:
        raise MusicBrainzError("down")


class MeasuredSpotify(FakeSpotify):
    def get_album_duration(self, album_id: str) -> dict:
        return {
            "album_id": album_id,
            "duration_ms": 2_700_000,
            "duration_minutes": 45.0,
            "release_date": "2001-06-01",
        }


def test_catalog_measures_duration_on_the_short_card() -> None:
    catalog = CatalogSearch(spotify=MeasuredSpotify(), musicbrainz=FakeMB())
    album = catalog.search_albums("trip hop", limit=5)["albums"][0]
    assert album["duration_minutes"] == 45.0
    assert album["duration_ms"] == 2_700_000
    assert album["year"] == 2001
    assert set(album) == {
        "album_id",
        "name",
        "artists",
        "year",
        "spotify_url",
        "duration_ms",
        "duration_minutes",
    }


def test_catalog_falls_back_when_musicbrainz_errors() -> None:
    catalog = CatalogSearch(spotify=SpotifyOnly(), musicbrainz=BoomMB())
    result = catalog.search_albums("electronic", limit=5)
    assert result["source"] == "spotify"
