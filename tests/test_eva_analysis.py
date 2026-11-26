from eva_data_analysis import text_to_duration


def test_text_to_duration_integer():
    """Test that a whole-hour duration is converted correctly."""
    assert text_to_duration("10:00") == 10


def test_text_to_duration_float():
    """Test that minutes are converted to a fraction of an hour."""
    assert text_to_duration("10:15") == 10.25