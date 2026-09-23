from __future__ import annotations

import os
import threading
import time
from typing import Any
from urllib.parse import urlparse

import httpx

from apps.workout_album.duration import ms_to_minutes, sum_duration_ms
from apps.workout_album.timing import log_elapsed

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
        self._token_lock = threading.Lock()
        self._covers: dict[str, str] = {}

    def configured(self) -> bool:
        return bool(self.client_id and self.client_secret)

    def search_albums(self, query: str, limit: int = 8) -> dict[str, Any]:
        limit = max(1, min(int(limit), 20))
        data = self._get("/search", {"q": query, "type": "album", "limit": limit})
        items = data.get("albums", {}).get("items") or []
        albums = []
        for item in items:
            if not item:
                continue
            self._remember_cover(item)
            albums.append(_compact_album(item))
        return {"query": query, "albums": albums}

    def get_album_tracks(self, album_id: str) -> dict[str, Any]:
        tracks: list[dict[str, Any]] = []
        offset = 0
        limit = 50
        # Own the page numbers. Following Spotify's `next` URL with params={}
        # makes httpx drop the query, so the first page repeats forever.
        for _ in range(20):
            payload = self._get(
                f"/albums/{album_id}/tracks",
                {"limit": limit, "offset": offset},
            )
            items = payload.get("items") or []
            if not items:
                break
            for item in items:
                tracks.append(
                    {
                        "id": item.get("id"),
                        "name": item.get("name"),
                        "duration_ms": int(item.get("duration_ms") or 0),
                        "track_number": item.get("track_number"),
                    }
                )
            total = payload.get("total")
            offset += len(items)
            if not isinstance(total, int) or offset >= total:
                break
        else:
            raise SpotifyError(f"Spotify track list for {album_id} did not end")
        return {"album_id": album_id, "tracks": tracks, "track_count": len(tracks)}

    def cover_for(self, album_id: str) -> str | None:
        """Cover seen while searching. One album GET only if that search missed it."""
        with self._token_lock:
            cached = self._covers.get(album_id)
        if cached:
            return cached
        try:
            album = self._get(f"/albums/{album_id}")
        except SpotifyError:
            return None
        self._remember_cover(album)
        with self._token_lock:
            return self._covers.get(album_id)

    def _remember_cover(self, item: dict[str, Any]) -> None:
        album_id = item.get("id")
        url = cover_url(item)
        if not album_id or not url:
            return
        with self._token_lock:
            self._covers[str(album_id)] = url

    def get_album_duration(self, album_id: str) -> dict[str, Any]:
        album = self._get(f"/albums/{album_id}")
        self._remember_cover(album)
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
        started = time.perf_counter()
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(
                url,
                params=params,
                headers={"Authorization": f"Bearer {token}"},
            )
        label = path if path.startswith("http") else path.split("?", 1)[0]
        log_elapsed(f"spotify GET {label}", started, str(response.status_code))
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
        with self._token_lock:
            now = time.time()
            if self._token and now < self._token_expires_at - 30:
                return self._token
            return self._fetch_token(now)

    def _fetch_token(self, now: float) -> str:
        started = time.perf_counter()
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                TOKEN_URL,
                data={"grant_type": "client_credentials"},
                auth=(self.client_id, self.client_secret),
            )
        log_elapsed("spotify POST /api/token", started, str(response.status_code))
        if response.status_code >= 400:
            raise SpotifyError(f"Spotify auth failed: {response.status_code} {response.text}")
        payload = response.json()
        self._token = payload["access_token"]
        self._token_expires_at = now + int(payload.get("expires_in") or 3600)
        return self._token


def cover_url(item: dict[str, Any]) -> str | None:
    """Spotify CDN cover near 640px, the size a 208pt disc needs at 3x."""
    images = [img for img in (item.get("images") or []) if isinstance(img, dict) and img.get("url")]
    sized = [img for img in images if isinstance(img.get("width"), int) and img["width"] > 0]
    ordered = sorted(sized, key=lambda img: abs(int(img["width"]) - 640)) if sized else images
    for img in ordered:
        url = _spotify_image_url(str(img.get("url") or ""))
        if url:
            return url
    return None


def _spotify_image_url(url: str) -> str | None:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https":
        return None
    if host != "i.scdn.co" and not host.endswith(".scdn.co"):
        return None
    return url


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
