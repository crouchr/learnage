#!/usr/bin/python3

import requests
import json
import julian
from pprint import pprint

import met_funcs
import ts_funcs

# Stockcross height is 129m
# https://getoutside.ordnancesurvey.co.uk/local/stockcross-west-berkshire


# Leave out daily forecast for now
# need to call this a couple of times in order to determine if pressure is rising, falling etc
def get_current_weather_info():
    """

    :return:
    """
    # Free version
    API_KEY = 'ab4b5be3e0bf875659c638ded9decd79'

    # Stockcross
    lat = "51.41460037"
    lon = "-1.37486378"

    url = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&appid=%s&units=metric&exclude=minutely,hourly,daily" % (lat, lon, API_KEY)

    weather_info = {}

    response = requests.get(url)
    data = json.loads(response.text)
    print(data)

    weather_info['lat']           = data['lat']
    weather_info['lon']           = data['lon']
    weather_info['tz']            = data['timezone']
    weather_info['tz_offset']     = data['timezone_offset']

    weather_info['ts_epoch']      = data['current']['dt']            # api = timestamp from the API in UNIX UTC
    weather_info['ts_local']      = ts_funcs.epoch_to_local(data['current']['dt'])
    weather_info['ts_utc']        = ts_funcs.epoch_to_utc(data['current']['dt'])

    weather_info['julian']        = julian.get_julian_date(weather_info['ts_utc'] )

    weather_info['sunrise_local'] = ts_funcs.epoch_to_local(data['current']['sunrise'])     # api = timestamp from the API in UNIX UTC
    weather_info['sunset_local']  = ts_funcs.epoch_to_local(data['current']['sunset'])      # api = timestamp from the API in UNIX UTC

    weather_info['pressure']      = data['current']['pressure']                 # api = sea-level hPa
    weather_info['wind_speed']    = round(met_funcs.m_per_sec_to_knots(data['current']['wind_speed'])  ,1)   # api = metres/s

    # api returns m/s
    weather_info['wind_strength'] = met_funcs.kph_to_beaufort(met_funcs.metres_per_sec_to_kph(data['current']['wind_speed'])) # metres/s

    # fixme : convert to wind quadrant e.g. NE and store as well as degrees
    weather_info['wind_deg']      = data['current']['wind_deg']

    weather_info['temp']          = round(data['current']['temp'], 1)
    weather_info['feels_like']    = round(data['current']['feels_like'], 1)
    weather_info['dew_point']     = round(data['current']['dew_point'], 1)
    weather_info['uvi']           = data['current']['uvi']          # Midday UV index
    weather_info['humidity']      = data['current']['humidity']     # percent
    weather_info['coverage']      = data['current']['clouds']       # percent
    weather_info['visibility']    = data['current']['visibility']   # average (metres)
    weather_info['location']      = "Stockcross, UK"                # how close ?

    # optional fields ?
    if 'wind_gust' in data['current']:
        weather_info['wind_gust']  = round(met_funcs.m_per_sec_to_knots(data['current']['wind_gust']) ,1)
    else:
        weather_info['wind_gust'] = "NULL"  # fixme = does this import into MySQL as a NULL ?

    if 'rain.1h' in data['current']:
        weather_info['rain']  = round(data['current']['rain.1h'], 1)      # rain volume for last hour (mm)
    else:
        weather_info['rain'] = 0.0

    # fixme - this is a list - so need to strore it as a list ? - store a assume a single item list for now until understand the API response more
    weather_info['main']          = data['current']['weather'][0]['main']
    weather_info['description']   = data['current']['weather'][0]['description']

    return weather_info



