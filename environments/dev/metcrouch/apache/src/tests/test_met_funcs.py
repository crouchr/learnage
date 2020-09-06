# author : R.Crouch
# Test met functions

import pytest
import met_funcs


@pytest.mark.parametrize(
    "mph, expected",
    [
        (0.0,  0.0),
        (1.0,  0.8690),
        (2.5,  2.1724),
        (10.0, 8.6898),
    ]
)
def test_mph_to_knots(mph, expected):
    knots = round(met_funcs.mph_to_knots(mph),4)
    assert knots == expected


@pytest.mark.parametrize(
    "kph, expected",
    [
        (0.0,  0.0),
        (1.0,  0.5400),
        (2.5,  1.3499),
        (10.0, 5.3996),
    ]
)
def test_kph_to_knots(kph, expected):
    knots = round(met_funcs.kph_to_knots(kph),4)
    assert knots == expected