import pytest
import forecaster


@pytest.mark.parametrize(
    "pressure, ptrend, wind_quadrant, expected_forecast",
    [
        (1023, "R", "NW", 1),
        (1023, "S", "NW", 2)
    ]
)
def test_forecaster(pressure, ptrend, wind_quadrant, expected_forecast):
    """

    :return:
    """
    forecast = forecaster.forecaster(pressure, ptrend, wind_quadrant)

    assert forecast == forecaster.forecast[expected_forecast]
