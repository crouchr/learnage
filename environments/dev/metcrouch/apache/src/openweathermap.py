#!/usr/bin/python3

import requests
import json
from pprint import pprint

# Stockcross height is 129m
# https://getoutside.ordnancesurvey.co.uk/local/stockcross-west-berkshire


# Leave out daily forecast for now
# need to call this a couple of times in order to determine if pressure is rising, falling etc
def get_current_weather_info():
    """

    :return:
    """
    API_KEY = 'ab4b5be3e0bf875659c638ded9decd79'
    lat = "51.41460037"
    lon = "-1.37486378"
    url = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&appid=%s&units=metric&exclude=minutely,hourly,daily" % (lat, lon, API_KEY)

    weather_info = {}

    response = requests.get(url)
    data = json.loads(response.text)
    print(data)

    weather_info['pressure']   = data['current']['pressure']
    weather_info['wind_speed'] = data['current']['wind_speed']
    weather_info['wind_deg']   = data['current']['wind_deg']

    return weather_info


if __name__ == '__main__':
    weather_info = get_current_weather_info()

    pprint(weather_info)
