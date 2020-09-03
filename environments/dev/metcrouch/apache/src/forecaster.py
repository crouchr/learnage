

forecast = []
forecast.append('Error')
forecast.append('Continued fair for 24 hours, lower temperature')
forecast.append('Continued fair for 48 hours, same temperature')




def map_pressure_to_coeff(pressure_str):
    """

    :param str pressure:
    :return:

    """
    pressure = int(pressure_str)
    if pressure <= 1008 :
        pressure_coeff = 3
    elif pressure >= 1023 :
        pressure_coeff = 1
    else:
        pressure_coeff = 2

    return pressure_coeff

def map_ptrend_to_coeff(ptrend_str):
    """
    Map 'Rising', ' Falling', 'Steady' to an integer
    :param str ptrend_str:
    :return:

    """
    ptrend_map = {
        'R' : 1,
        'S' : 2,
        'F' : 3
    }
    ptrend = ptrend_str[0].upper()
    ptrend_coeff = ptrend_map[ptrend]

    return ptrend_coeff


def map_wind_dir_to_coeff(wind_dir_str):
    """

    :param wind_dir_str:
    :return:
    """

    wind_dir_map = {
        'N'   : 1,
        'NNE' : 4,
        'NE'  : 4,
        'ENE' : 4,
        'E'   : 4,
        'ESE' : 3,
        'SE'  : 3,
        'SSE' : 3,
        'S'   : 2,
        'SSW' : 2,
        'SW'  : 2,
        'WSW' : 2,
        'W'   : 1,
        'WNW' : 1,
        'NW'  : 1,
        'NNW' : 1
    }

    wind_dir = wind_dir_str.upper()
    wind_dir_coeff = wind_dir_map[wind_dir]

    return wind_dir_coeff


def get_forecaster_index(pressure_coeff, ptrend_coeff, wind_dir_coeff):
    """
    Forecast next n hours based on pressure, trend and wind quadrant
    :param int pressure_coeff:
    :param int ptrend_coeff:
    :param int wind_dir_coeff:
    :return: str Text containing forecast
    """

    forecast_index = ((pressure_coeff - 1) * 3) + ptrend_coeff + ((wind_dir_coeff -1) * 9)

    return forecast_index
