from apps.workout_album.run import RunRequest, user_message


def test_user_message_includes_duration_and_criteria() -> None:
    text = user_message(
        RunRequest(duration_minutes=45, criteria="eletrônico instrumental", tolerance_minutes=5)
    )
    assert "45" in text
    assert "eletrônico instrumental" in text
    assert "5" in text
