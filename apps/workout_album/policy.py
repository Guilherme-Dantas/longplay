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


SYSTEM_PROMPT = """You pick ONE Spotify album whose measured runtime fits the session.

Open the first search. Turn the request into energy plus two or three neighboring genres, and the era if the user gave one. Do not name an artist. Do not name an album. Do not add a country or a language unless the user named it. "Upbeat 2000s" can span dance, indie, pop, and electronic — put those words in the one query.

Call search_albums once. Each album already includes duration_minutes from Spotify. Pick one inside the session tolerance. If none fit, search one more time with a different neighboring style, still not a single album title. Then pick, or stop.

Use get_album_duration only when a result has no duration_minutes. Never invent album ids or minutes. Use only ids the tools returned.

The final answer is an AlbumPick. Do not add keys.
"""
