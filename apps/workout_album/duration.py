from __future__ import annotations


def sum_duration_ms(tracks: list[dict]) -> int:
    """Deterministic album length. The model must not invent this."""
    return sum(int(track.get("duration_ms") or 0) for track in tracks)


def ms_to_minutes(duration_ms: int) -> float:
    return round(duration_ms / 60_000, 2)


def within_tolerance(
    duration_ms: int, target_minutes: float, tolerance_minutes: float
) -> bool:
    target_ms = target_minutes * 60_000
    delta_ms = abs(duration_ms - target_ms)
    return delta_ms <= tolerance_minutes * 60_000
