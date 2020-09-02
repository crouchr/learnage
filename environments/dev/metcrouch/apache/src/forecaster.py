

forecast = []
forecast.append('Error')
forecast.append('Continued fair for 24 hours, lower temperature')
forecast.append('Continued fair for 48 hours, same temperature')


def forecaster(pressure, ptrend, wind_quadrant):
    """
    Forecast next n hours based on pressure, trend and wind quadrant
    :param int pressure:
    :param str ptrend:
    :param str wind_quadrant:
    :return: str Text containing forecast
    """

    if pressure > 1013:
        tag = 1
    else:
        tag = 2

    return forecast[tag]
