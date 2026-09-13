from __future__ import annotations

import re
import unicodedata


def normalize_name(value: str) -> str:
    text = unicodedata.normalize("NFKD", value or "")
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[\(\[].*?[\)\]]", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def _token_overlap(left: str, right: str) -> float:
    a = set(normalize_name(left).split())
    b = set(normalize_name(right).split())
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def score_album(
    wanted_title: str,
    wanted_artist: str,
    candidate_title: str,
    candidate_artists: list[str],
) -> float:
    title_score = _token_overlap(wanted_title, candidate_title)
    artist_blob = " ".join(candidate_artists)
    artist_score = _token_overlap(wanted_artist, artist_blob)
    return (0.65 * title_score) + (0.35 * artist_score)


def pick_spotify_match(
    wanted_title: str,
    wanted_artist: str,
    candidates: list[dict],
    *,
    min_score: float = 0.45,
) -> dict | None:
    ranked: list[tuple[float, dict]] = []
    for item in candidates:
        score = score_album(
            wanted_title,
            wanted_artist,
            str(item.get("name") or ""),
            list(item.get("artists") or []),
        )
        if score >= min_score:
            ranked.append((score, item))
    if not ranked:
        return None
    ranked.sort(key=lambda pair: pair[0], reverse=True)
    return ranked[0][1]
