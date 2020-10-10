# This is not used - it could be deleted
import pytest

import differentiate


# ----------
@pytest.mark.parametrize(
    "numbers, expected",
    [
        ([1,3,8], [0, 2,5]),
    ]
)
def test_differentiate(numbers, expected):
    numbers_diff = differentiate.differentiate(numbers)
    assert numbers_diff == expected
