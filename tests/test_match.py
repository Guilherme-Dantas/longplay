from apps.workout_album.match import pick_spotify_match, score_album


def test_exact_title_and_artist_wins() -> None:
    candidates = [
        {
            "album_id": "wrong",
            "name": "Random LP",
            "artists": ["Someone"],
        },
        {
            "album_id": "right",
            "name": "Dummy",
            "artists": ["Portishead"],
        },
    ]
    match = pick_spotify_match("Dummy", "Portishead", candidates)
    assert match is not None
    assert match["album_id"] == "right"


def test_rejects_unrelated_candidate() -> None:
    candidates = [{"album_id": "x", "name": "Greatest Hits", "artists": ["Various"]}]
    assert pick_spotify_match("Mezzanine", "Massive Attack", candidates) is None


def test_score_prefers_title_overlap() -> None:
    close = score_album("Dummy", "Portishead", "Dummy", ["Portishead"])
    far = score_album("Dummy", "Portishead", "Third", ["Portishead"])
    assert close > far
