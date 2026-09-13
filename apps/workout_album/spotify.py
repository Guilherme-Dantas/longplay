from __future__ import annotations

import os
import time
from typing import Any

import httpx

from apps.workout_album.duration import ms_to_minutes, sum_duration_ms

TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE = "https://api.spotify.com/v1"


class SpotifyError(RuntimeError):
    pass


class SpotifyClient:
    """Client-credentials catalog access. No user OAuth."""

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        timeout: float = 20.0,
    ) -> None:
        self.client_id = client_id or os.environ.get("SPOTIFY_CLIENT_ID", "").strip()
        self.client_secret = client_secret or os.environ.get("SPOTIFY_CLIENT_SECRET", "").strip()
        self.timeout = timeout
        self._token: str | None = None
        self._token_expires_at = 0.0

    def configured(self) -> bool:
        return bool(self.client_id and self.client_secret)

    def search_albums(self, query: str, limit: int = 8) -> dict[str, Any]:
        limit = max(1, min(int(limit), 20))
        data = self._get("/search", {"q": query, "type": "album", "limit": limit})
        items = data.get("albums", {}).get("items") or []
        albums = [_compact_album(item) for item in items if item]
        return {"query": query, "albums": albums}

    def get_album_tracks(self, album_id: str) -> dict[str, Any]:
        tracks: list[dict[str, Any]] = []
        path = f"/albums/{album_id}/tracks"
        params: dict[str, Any] = {"limit": 50}
        while path:
            payload = self._get(path, params)
            params = {}
            for item in payload.get("items") or []:
                tracks.append(
                    {
                        "id": item.get("id"),
                        "name": item.get("name"),
                        "duration_ms": int(item.get("duration_ms") or 0),
                        "track_number": item.get("track_number"),
                    }
                )
            next_url = payload.get("next")
            path = next_url or ""
        return {"album_id": album_id, "tracks": tracks, "track_count": len(tracks)}

    def get_album_duration(self, album_id: str) -> dict[str, Any]:
        album = self._get(f"/albums/{album_id}")
        tracks_payload = self.get_album_tracks(album_id)
        duration_ms = sum_duration_ms(tracks_payload["tracks"])
        return {
            **_compact_album(album),
            "duration_ms": duration_ms,
            "duration_minutes": ms_to_minutes(duration_ms),
            "track_count": tracks_payload["track_count"],
        }

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        token = self._access_token()
        url = path if path.startswith("http") else f"{API_BASE}{path}"
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(
                url,
                params=params,
                headers={"Authorization": f"Bearer {token}"},
            )
        if response.status_code >= 400:
            raise SpotifyError(f"Spotify GET {path} failed: {response.status_code} {response.text}")
        return response.json()

    def _access_token(self) -> str:
        if not self.configured():
            raise SpotifyError(
                "Spotify is not configured. Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET."
            )
        now = time.time()
        if self._token and now < self._token_expires_at - 30:
            return self._token
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                TOKEN_URL,
                data={"grant_type": "client_credentials"},
                auth=(self.client_id, self.client_secret),
            )
        if response.status_code >= 400:
            raise SpotifyError(f"Spotify auth failed: {response.status_code} {response.text}")
        payload = response.json()
        self._token = payload["access_token"]
        self._token_expires_at = now + int(payload.get("expires_in") or 3600)
        return self._token


def _compact_album(item: dict[str, Any]) -> dict[str, Any]:
    artists = [artist.get("name") for artist in (item.get("artists") or []) if artist.get("name")]
    external = item.get("external_urls") or {}
    return {
        "album_id": item.get("id"),
        "name": item.get("name"),
        "artists": artists,
        "total_tracks": item.get("total_tracks"),
        "release_date": item.get("release_date"),
        "spotify_url": external.get("spotify") or f"https://open.spotify.com/album/{item.get('id')}",
    }
