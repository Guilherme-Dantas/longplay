from __future__ import annotations

from pydantic import BaseModel, Field

from harness.policy import Policy


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
- Call search_albums with a query derived from the user's criteria.
- Call get_album_duration on candidate albums until you find one whose duration is within the requested tolerance.
- If none fit, search again with a different query (live album, compilation, shorter EP vs LP) before giving up.
- Duration is the sum of tracks from the tool. Do not estimate minutes yourself.
- Rank albums that already fit the duration by the listening criteria (genre, vocal/instrumental, energy, language, etc.).
- Reply with a single JSON object matching AlbumPick. No markdown, no extra keys.

AlbumPick:
{"album_id": str, "name": str, "artists": [str], "duration_ms": int, "duration_minutes": float, "reason": str, "spotify_url": str}
"""


def build_policy() -> Policy:
    return Policy(
        name="workout_album",
        system_prompt=SYSTEM_PROMPT,
        max_steps=8,
        output_schema=AlbumPick,
        repair_attempts=1,
    )
