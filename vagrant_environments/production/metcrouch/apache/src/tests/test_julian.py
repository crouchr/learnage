import pytest

import julian


# ----------
@pytest.mark.parametrize(
    "date_str, expected",
    [
        ("2012-11-7 18:00:00",  2456238),
        ("2012-11-8 18:00:00",  2456239)
    ]
)
def test_get_julian_date(date_str, expected):
    jd = julian.get_julian_date(date_str)
    assert jd == expected
