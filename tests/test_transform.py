from consultant_pulse.transform import normalize_score


def test_normalize_score_clamps_high_values():
    assert normalize_score(9) == 5.0


def test_normalize_score_clamps_low_values():
    assert normalize_score(0) == 1.0


def test_normalize_score_none():
    assert normalize_score(None) is None
