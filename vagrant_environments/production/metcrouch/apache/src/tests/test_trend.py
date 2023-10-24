import pytest

import trend


@pytest.mark.parametrize(
    "values, expected",
    [
        ([1010, 1020, 1030, 1040, 1050], "Rising"),
        ([1010, 1010, 1010, 1010, 1010], "Steady"),
        ([1050, 1040, 1030, 1020, 1010], "Falling"),
        ([1022, 1022, 1023, 1023, 1023], "Rising"),
    ]
)
def test_trendline(values, expected):
    index = [1,2,3,4,5]
    trend_str, slope = trend.trendline(index, values)
    assert trend_str == expected
