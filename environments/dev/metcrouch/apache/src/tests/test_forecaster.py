import pytest
import forecaster


@pytest.mark.parametrize(
    "pressure_str, expected",
    [
        ("999", 3),
        ("1008", 3),
        ("1009", 2),
        ("1022", 2),
        ("1023", 1),
        ("1024", 1),
    ]
)
def test_map_pressure_to_coeff(pressure_str, expected):
    coeff = forecaster.map_pressure_to_coeff(pressure_str)
    assert coeff == expected


@pytest.mark.parametrize(
    "ptrend_str, expected",
    [
        ("Rising",  1),
        ("Steady",  2),
        ("Falling", 3),
        ("rising",  1),
        ("steady",  2),
        ("falling", 3),
    ]
)
def test_map_ptrend_to_coeff(ptrend_str, expected):
    coeff = forecaster.map_ptrend_to_coeff(ptrend_str)
    assert coeff == expected


@pytest.mark.parametrize(
    "wind_dir_str, expected",
    [
        ("N",  1),
        ("NE", 4),
        ("E",  4),
        ("SE", 3),
        ("S",  2),
        ("SW", 2),
        ("W",  1),
        ("NW", 1)
    ]
)
def test_map_wind_dir_to_coeff(wind_dir_str, expected):
    coeff = forecaster.map_wind_dir_to_coeff(wind_dir_str)
    assert coeff == expected


#@pytest.mark.parametrize(
#    "pressure, ptrend, wind_quadrant, expected_forecast",
#    [
#        (1023, "R", "NW", 1),
#        (1023, "S", "NW", 2)
#    ]
#)
#def test_forecaster(pressure, ptrend, wind_quadrant, expected_forecast):
#    """
#
#    :return:
#    """
#    forecast = forecaster.forecaster(pressure, ptrend, wind_quadrant)
#
#    assert forecast == forecaster.forecast[expected_forecast]
