#!/usr/bin/python3
# Stockcross height is 129m
# https://getoutside.ordnancesurvey.co.uk/local/stockcross-west-berkshire

import time
from pprint import pprint

import current_weather
import connect_db
import locations

def insert_rec_to_db(mydb, mycursor, weather_info):
    """
    Insert record into database
    :param weather_info:
    :return:
    """

    sql = "INSERT INTO actual (" \
          "ts_local, " \
          "ts_utc, " \
          "julian, " \
          "hour_utc, " \
          "location, " \
          "main, " \
          "description, " \
          "pressure, " \
          "wind_speed, " \
          "wind_deg, " \
          "wind_quadrant, " \
          "wind_strength, " \
          "wind_gust, " \
          "temp, " \
          "feels_like, " \
          "dew_point, " \
          "uvi, " \
          "humidity, " \
          "coverage, " \
          "visibility, " \
          "rain, " \
          "snow, " \
          "source," \
          "lat, " \
          "lon, " \
          "tz, " \
          "tz_offset, " \
          "ts_epoch, " \
          "sunrise_local, " \
          "sunset_local" \
          ") " \
          "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    val = (weather_info['ts_local'],
           weather_info['ts_utc'],
           weather_info['julian'],
           weather_info['hour_utc'],
           weather_info['location'],
           weather_info['main'],
           weather_info['description'],
           weather_info['pressure'],
           weather_info['wind_speed'],
           weather_info['wind_deg'],
           weather_info['wind_quadrant'],
           weather_info['wind_strength'],
           weather_info['wind_gust'],
           weather_info['temp'],
           weather_info['feels_like'],
           weather_info['dew_point'],
           weather_info['uvi'],
           weather_info['humidity'],
           weather_info['coverage'],
           weather_info['visibility'],
           weather_info['rain'],
           weather_info['snow'],
           weather_info['source'],
           weather_info['lat'],
           weather_info['lon'],
           weather_info['tz'],
           weather_info['tz_offset'],
           weather_info['ts_epoch'],
           weather_info['sunrise_local'],
           weather_info['sunset_local']
           )

    mycursor.execute(sql, val)
    mydb.commit()
    print(mycursor.rowcount, "record inserted in MySQL OK")


def main():

    for place in locations.locations:
        print(place['location'])

    mydb, mycursor = connect_db.connect_database("metminidb")

    while True:
        print("-----------------")
        print("Local time (not UTC) : " + time.ctime())
        for place in locations.locations:
            weather_info = current_weather.get_current_weather_info(place['location'], place['lat'], place['lon'])
            pprint(weather_info)
            insert_rec_to_db(mydb, mycursor, weather_info)

        print("waiting...")
        time.sleep(600)         # poll every 10 minutes


if __name__ == '__main__':
    main()

