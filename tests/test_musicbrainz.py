from apps.workout_album.musicbrainz import taste_to_mb_query


def test_taste_query_adds_tag_clauses() -> None:
    query = taste_to_mb_query("electronic instrumental")
    assert 'tag:"electronic"' in query
    assert 'tag:"instrumental"' in query
    assert "primarytype:album" in query


def test_taste_query_keeps_lucene_passthrough() -> None:
    query = taste_to_mb_query('tag:"trip hop"')
    assert 'tag:"trip hop"' in query
    assert "primarytype:album" in query
