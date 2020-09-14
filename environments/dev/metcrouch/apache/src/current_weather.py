#!/usr/bin/python3


import requests
import json
import julian
import time
from pprint import pprint

import met_funcs
import ts_funcs

# Stockcross height is 129m
# https://getoutside.ordnancesurvey.co.uk/local/stockcross-west-berkshire


# Leave out daily forecast for now
# need to call this a couple of times in order to determine if pressure is rising, falling etc
def get_current_weather_info(location, lat, lon):
    """

    :return:
    """
    # Free version - FIXME : read from an ENV var
    API_KEY = 'ab4b5be3e0bf875659c638ded9decd79'
    url = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&appid=%s&units=metric&exclude=minutely,hourly,daily" % (lat, lon, API_KEY)

    try:
        weather_info = {}

        response = requests.get(url)
        data = json.loads(response.text)
        print(data)
        time.sleep(2)           # crude rate limit

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

        weather_info['wind_deg']      = data['current']['wind_deg']
        weather_info['wind_quadrant'] = met_funcs.wind_deg_to_quadrant(weather_info['wind_deg'])
        weather_info['temp']          = round(data['current']['temp'], 1)
        weather_info['feels_like']    = round(data['current']['feels_like'], 1)
        weather_info['dew_point']     = round(data['current']['dew_point'], 1)
        weather_info['humidity']      = data['current']['humidity']     # percent
        weather_info['coverage']      = data['current']['clouds']       # percent
        weather_info['visibility']    = data['current']['visibility']   # average (metres)
        weather_info['location']      = location                        # how close ?

    # optional fields ?
        if 'wind_gust' in data['current']:
            weather_info['wind_gust']  = round(met_funcs.m_per_sec_to_knots(data['current']['wind_gust']) ,1)
        else:
            weather_info['wind_gust'] = "NULL"  # fixme = does this import into MySQL as a NULL ?

        if 'rain.1h' in data['current']:
            weather_info['rain']  = round(data['current']['rain.1h'], 1)      # rain volume for last hour (mm)
        else:
            weather_info['rain'] = 0.0

        if 'snow.1h' in data['current']:
            weather_info['snow']  = round(data['current']['snow.1h'], 1)      # snow volume for last hour (mm)
        else:
            weather_info['snow'] = 0.0

        if 'uvi' in data['current']:
            weather_info['uvi'] = data['current']['uvi']  # Midday UV index
        else:
            weather_info['uvi'] = -99.9                     # -99.9 = missing data

        # fixme - this is a list - so need to store it as a list ? - store a assume a single item list for now until understand the API response more
        weather_info['main']          = data['current']['weather'][0]['main']
        weather_info['description']   = data['current']['weather'][0]['description']

    except Exception as e:
        print(e)


    return weather_info
