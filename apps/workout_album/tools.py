from __future__ import annotations

from apps.workout_album.spotify import SpotifyClient
from harness.tools import ToolRegistry


def build_spotify_tools(client: SpotifyClient | None = None) -> ToolRegistry:
    spotify = client or SpotifyClient()
    tools = ToolRegistry()

    @tools.tool(
        description=(
            "Search the Spotify catalog for albums. Returns id, name, artists, "
            "total_tracks, release_date, and spotify_url. Does not include duration."
        )
    )
    def search_albums(query: str, limit: int = 8) -> dict:
        return spotify.search_albums(query=query, limit=limit)

    @tools.tool(
        description="List tracks for an album id, including each track duration_ms."
    )
    def get_album_tracks(album_id: str) -> dict:
        return spotify.get_album_tracks(album_id=album_id)

    @tools.tool(
        description=(
            "Sum track durations for an album id. Use this before recommending. "
            "Never guess album length."
        )
    )
    def get_album_duration(album_id: str) -> dict:
        return spotify.get_album_duration(album_id=album_id)

    return tools
