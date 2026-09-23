from __future__ import annotations

import time
from typing import Any

import httpx

from apps.workout_album.timing import log_elapsed

MB_BASE = "https://musicbrainz.org/ws/2"
USER_AGENT = "longplay/0.1.0 (https://github.com/Guilherme-Dantas/longplay)"


class MusicBrainzError(RuntimeError):
    pass


class MusicBrainzClient:
    """Discovery catalog: tags and titles. Not the playback source."""

    def __init__(self, timeout: float = 20.0) -> None:
        self.timeout = timeout

    def search_release_groups(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        limit = max(1, min(int(limit), 10))
        payload = self._get(
            "/release-group",
            {"query": taste_to_mb_query(query), "fmt": "json", "limit": limit},
        )
        groups = payload.get("release-groups") or []
        hits: list[dict[str, Any]] = []
        for group in groups:
            artist = _first_artist(group)
            title = (group.get("title") or "").strip()
            if not title or not artist:
                continue
            hits.append(
                {
                    "title": title,
                    "artist": artist,
                    "mbid": group.get("id"),
                    "tags": [tag.get("name") for tag in (group.get("tags") or []) if tag.get("name")],
                    "primary_type": group.get("primary-type"),
                }
            )
        return hits

    def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        url = f"{MB_BASE}{path}"
        started = time.perf_counter()
        try:
            with httpx.Client(timeout=self.timeout, headers={"User-Agent": USER_AGENT}) as client:
                response = client.get(url, params=params)
        except httpx.HTTPError as exc:
            log_elapsed(f"musicbrainz GET {path}", started, "error")
            raise MusicBrainzError(f"MusicBrainz GET {path} failed: {exc}") from exc
        log_elapsed(f"musicbrainz GET {path}", started, str(response.status_code))
        if response.status_code >= 400:
            raise MusicBrainzError(
                f"MusicBrainz GET {path} failed: {response.status_code} {response.text}"
            )
        return response.json()


def taste_to_mb_query(query: str) -> str:
    """Turn free-text listening taste into a MusicBrainz Lucene query.

    Spotify album search cannot filter by genre. MusicBrainz can, via tags.
    Keep albums (not singles) in the result set.
    """
    raw = " ".join((query or "").split())
    album = "primarytype:album"
    if not raw:
        return album
    if ":" in raw:
        return f"({raw}) AND {album}"
    tokens = [_lucene_term(token) for token in raw.split() if _lucene_term(token)]
    if not tokens:
        return album
    tags = " OR ".join(f'tag:"{token}"' for token in tokens)
    return f"(({raw}) OR ({tags})) AND {album}"


def _lucene_term(token: str) -> str:
    return token.replace("\\", "").replace('"', "").strip()


def _first_artist(group: dict[str, Any]) -> str:
    credits = group.get("artist-credit") or []
    for credit in credits:
        if isinstance(credit, dict):
            artist = credit.get("name") or (credit.get("artist") or {}).get("name")
            if artist:
                return str(artist)
        elif isinstance(credit, str) and credit.strip():
            return credit.strip()
    return ""
