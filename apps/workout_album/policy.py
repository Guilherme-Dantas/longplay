from __future__ import annotations

from pydantic import BaseModel, Field


class AlbumPick(BaseModel):
    album_id: str
    name: str
    artists: list[str]
    duration_ms: int
    duration_minutes: float
    reason: str = Field(description="Why this album fits the session and criteria")
    spotify_url: str


SYSTEM_PROMPT = """You pick ONE Spotify album for a workout session.

Hard rules:
- Always use tools. Never invent album ids, names, or durations.
- Call search_albums with a query derived from the user's criteria (genre, instrumental, era).
- search_albums looks up MusicBrainz first, then finds the same record on Spotify by name. Use only the returned Spotify album_id values.
- Call get_album_duration on those Spotify ids until one fits the session tolerance.
- If none fit, search again with a different query (live album, compilation, shorter EP vs LP) before giving up.
- Duration is the sum of tracks from the tool. Do not estimate minutes yourself.
- Rank albums that already fit the duration by the listening criteria (genre, vocal/instrumental, energy, language, etc.).
- The final answer is an AlbumPick. Do not add keys.
"""
