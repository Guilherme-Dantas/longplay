from apps.workout_album.duration import ms_to_minutes, sum_duration_ms, within_tolerance


def test_sum_duration_ms() -> None:
    tracks = [{"duration_ms": 180_000}, {"duration_ms": 120_000}, {"duration_ms": None}]
    assert sum_duration_ms(tracks) == 300_000


def test_ms_to_minutes() -> None:
    assert ms_to_minutes(2_700_000) == 45.0


def test_within_tolerance() -> None:
    forty_five = 45 * 60_000
    assert within_tolerance(forty_five, 45, 5)
    assert within_tolerance(forty_five + 4 * 60_000, 45, 5)
    assert not within_tolerance(forty_five + 12 * 60_000, 45, 5)
