# https://realpython.com/python-time-module/
# https://www.epochconverter.com/   - use this online tool to convert to/from epoch in a web service
# timedatectl - run on CentOS7 to see UTC and local time and TZ settings
# triggered by cron to run once a day

from datetime import datetime
import time

import forecaster
import connect_db
import trend
import met_funcs
import ts_funcs
import locations
import julian
import twitter

def get_forecast_prereqs(location, julian_day_yesterday, forecast_hour_utc, source):
    """
    Retrieve the required values needed to make a forecast from the database
    :return:
    """
    pressure_values = []
    wind_deg_values = []
    wind_strength_values = []

    recs_to_retrieve = 3    # number of readings to use to determine pressure trend and wind_deg
    index = [1, 2, 3]       # FIXME : calc from recs_to_retrieve

    mydb, mycursor = connect_db.connect_database("metminidb")

    # Retrieve the FIRST set of records that are AFTER the 0900 UTC optimaum forecasting time
    sql_query = """SELECT * FROM actual WHERE location = %s and julian = %s and hour_utc >= %s and source = "OpenWeatherMap" limit %s"""
    mycursor.execute(sql_query, (location, julian_day_yesterday, forecast_hour_utc, recs_to_retrieve,))
    records = mycursor.fetchall()

    if len(records) != recs_to_retrieve:
        print("Unable to retrieve records from database")
        return None, None, None, None, None

    # fixme : fragile = need named columns not numbers
    for row in records:
        pressure_values.append(row[8])
        wind_deg_values.append(row[10])
        wind_strength_values.append(row[12])

    trend_str, slope = trend.trendline(index, pressure_values)
    wind_deg_avg = int(sum(wind_deg_values)) / len(wind_deg_values)
    wind_deg_avg = int(wind_deg_avg)

    wind_strength_avg = int(sum(wind_strength_values)) / len(wind_strength_values)
    wind_strength     = int(wind_strength_avg)

    pressure = pressure_values[0]   # use the first one
    ptrend = trend_str
    wind_quadrant = met_funcs.wind_deg_to_quadrant(wind_deg_avg)

    return pressure, ptrend, wind_quadrant, wind_strength, slope


# FIXME : something is wrong here but go with it
# use forecast_hour_utc = 10 to get it to work for now
def calc_forecast_time_epoch(forecast_hour_utc):
    """
    Calculate UNIX epoch (UTC/GMT) for when forecast should be made - this is 09:00 UTC
    :return:
    """
    utc_now = datetime.now()    # FIXME : should this be datetime.utcnow() ?
    utc_now_epoch = int(utc_now.timestamp())

    forecast_ts = utc_now.replace(hour=forecast_hour_utc, minute=0, second=0, microsecond=0)
    forecast_ts_utc = int(forecast_ts.timestamp())

    return forecast_ts_utc


# def sleep_till_forecast_time(utc_hour_required, utc_minute_required):
#     """
#     Sleep until 0900 UTC
#     """
#     sleep_period = 60
#
#     while True:
#         print('-----')
#         now = time.time()
#         utc_now = datetime.utcnow()
#         print("Local time : " + time.ctime())
#         #print(datetime.timestamp(utc_now))
#         utc_hour   = utc_now.hour
#         utc_minute = utc_now.minute
#         utc_second = utc_now.second
#         print("UTC hour   : " + utc_hour.__str__())
#         print("UTC minute : " + utc_minute.__str__())
#         print("UTC second : " + utc_second.__str__())
#
#         if utc_hour >= utc_hour_required and utc_minute >= utc_minute_required:
#             return
#
#         msg = "Waiting for hour>=" + utc_hour_required.__str__() + ", minute>=" + utc_minute_required.__str__() + " ..."
#         print(msg)
#         time.sleep(sleep_period)
#
#     return


def add_forecast_to_db(julian_day, location, pressure, ptrend, wind_quadrant, wind_strength, slope, source, forecast_text):
    """
    :param julian_day: When the forecast was made for
    :param pressure:
    :param ptrend:
    :param wind_quadrant:
    :param wind_strength:
    :param slope: pressure trend slope value
    :param forecast_text:
    :return:
    """
    utc_epoch = time.time()
    #print(utc_epoch)

    mydb, mycursor = connect_db.connect_database("metminidb")

    ts_local = ts_funcs.epoch_to_local(utc_epoch)
    ts_utc   = ts_funcs.epoch_to_utc(utc_epoch)

    sql = "INSERT INTO forecasts (" \
          "ts_local, " \
          "ts_utc, " \
          "julian, " \
          "location, " \
          "pressure, " \
          "ptrend, " \
          "wind_quadrant, " \
          "wind_strength, " \
          "slope, " \
          "source, " \
          "forecast" \
          ") " \
          "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    val = (ts_local,
           ts_utc,
           julian_day,
           location,
           pressure,
           ptrend,
           wind_quadrant,
           wind_strength,
           slope,
           source,
           forecast_text
           )

    mycursor.execute(sql, val)
    mydb.commit()
    message = "record inserted in MySQL OK for location=" + location.__str__()
    print(mycursor.rowcount, message)

# ---------------------------------------------------

# Manually run this at 10 UTC - then do via Cron
def main():
    source = "OpenWeatherMap"       # the only source of weather info at the moment
    forecast_hour_utc = 9          # FIXME : Test purposes

    try:
        now_utc = time.time()
        utc_time_str = ts_funcs.epoch_to_utc(now_utc)

        julian_day = julian.get_julian_date(utc_time_str)
        julian_day_yesterday = julian_day - 1

        for place in locations.locations:
            print("===========================================================")
            print("Location : " + place['location'])

            pressure, ptrend, wind_quadrant, wind_strength, slope = \
                get_forecast_prereqs(place['location'], julian_day_yesterday, forecast_hour_utc, source)

            forecast_text = forecaster.get_forecaster_text(pressure, ptrend, wind_quadrant, wind_strength)
            full_forecast_txt = ""
            full_forecast_txt += place['location'] + "\n"
            full_forecast_txt += "Next 12 hours : " + forecast_text
            full_forecast_txt += "\n"
            full_forecast_txt += "{"
            full_forecast_txt += "pressure=" + pressure.__str__() + " mbar (" + ptrend + "), wind=" + wind_quadrant + "/F" + wind_strength.__str__()
            full_forecast_txt += ", pressure_slope=" + slope.__str__()
            full_forecast_txt += "}"
            print("------------------------------------------------")
            print(full_forecast_txt)
            print("------------------------------------------------")

            add_forecast_to_db(julian_day, place['location'], pressure, ptrend, wind_quadrant, wind_strength, slope, source, forecast_text)

            # only Tweet out my local forecast
            if place['location'] == "Stockcross, UK":
                twitter.send_tweet(full_forecast_txt)

            print()

    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
