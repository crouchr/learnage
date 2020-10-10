# author : R.Crouch
# Test met functions

import pytest
import met_funcs


# ----------
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


# ----------
@pytest.mark.parametrize(
    "m_per_sec, expected",
    [
        (0.0,  0.0),
        (1.0,  1.9438),
        (2.5,  4.8596),
        (10.0, 19.4384),
    ]
)
def test_m_per_sec_to_knots(m_per_sec, expected):
    knots = round(met_funcs.m_per_sec_to_knots(m_per_sec),4)
    assert knots == expected


# ----------
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


# ----------
@pytest.mark.parametrize(
    "kph, expected",
    [
        (0.0,  0),
        (1.0,  0),
        (2.5,  1),
        (7.1,  2),
        (15.3, 3),
        (25.3, 4),
    ]
)
def test_kph_to_beaufort(kph, expected):
    beaufort = round(met_funcs.kph_to_beaufort(kph), 4)
    assert beaufort == expected


# ----------
@pytest.mark.parametrize(
    "m_per_sec, expected",
    [
        (0.0,  0),
        (1.0,  3.6),
        (5.1, 18.36),
        (10.0, 36.0),
    ]
)
def test_kph_to_beaufort(m_per_sec, expected):
    kph = round(met_funcs.metres_per_sec_to_kph(m_per_sec), 4)
    assert kph == expected


# ----------
@pytest.mark.parametrize(
    "wind_deg, expected",
    [
        (0,  "NE"),
        (45, "NE"),
        (90, "NE"),
        (91, "SE"),

        (135, "SE"),
        (179, "SE"),
        (180,"SW"),
        (360, "NE"),
    ]
)
def test_wind_deg_to_quadrant(wind_deg, expected):
    wind_quadrant = met_funcs.wind_deg_to_quadrant(wind_deg)
    assert wind_quadrant == expected


# ----------
@pytest.mark.parametrize(
    "wind_dir, expected",
    [
        ("N",  "NE"),
    ]
)
def wind_dir_to_quadrant(wind_dir, expected):
    wind_quadrant = met_funcs.wind_deg_to_quadrant(wind_dir)
    assert wind_quadrant == expected


