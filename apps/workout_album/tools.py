from __future__ import annotations

from apps.workout_album.catalog import CatalogSearch
from apps.workout_album.spotify import SpotifyClient
from harness.tools import ToolRegistry


def build_spotify_tools(client: SpotifyClient | None = None) -> ToolRegistry:
    spotify = client or SpotifyClient()
    catalog = CatalogSearch(spotify=spotify)
    tools = ToolRegistry()

    @tools.tool(
        description=(
            "Find albums matching listening taste. Discovers candidates in MusicBrainz, "
            "then resolves each to a Spotify album by title and artist. Returns Spotify "
            "id, name, artists, total_tracks, release_date, and spotify_url. "
            "Does not include duration — call get_album_duration next."
        )
    )
    def search_albums(query: str, limit: int = 8) -> dict:
        return catalog.search_albums(query=query, limit=limit)

    @tools.tool(
        description="List tracks for a Spotify album id, including each track duration_ms."
    )
    def get_album_tracks(album_id: str) -> dict:
        return spotify.get_album_tracks(album_id=album_id)

    @tools.tool(
        description=(
            "Sum Spotify track durations for an album id. Use this before recommending. "
            "Never guess album length."
        )
    )
    def get_album_duration(album_id: str) -> dict:
        return spotify.get_album_duration(album_id=album_id)

    return tools
