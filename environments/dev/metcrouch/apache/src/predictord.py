# https://realpython.com/python-time-module/
# https://www.epochconverter.com/   - use this online tool to convert to/from epoch in a web service
# timedatectl - run on CentOS7 to see UTC and local time and TZ settings

from datetime import datetime
import time

import forecaster
import connect_db
import trend
import met_funcs
import ts_funcs


def get_forecast_prereqs(forecast_hour_utc):
    """
    Retrieve the required values needed to make a forecast from the database
    :return:
    """
    pressure_values = []
    wind_deg_values = []

    recs_to_retrieve = 3    # number of readings to use to determine pressure trend and wind_deg
    index = [1, 2, 3]       # FIXME : calc from recs_to_retrieve

    forecast_ts_utc = calc_forecast_time_epoch(forecast_hour_utc)

    print(forecast_ts_utc)

    #while True:
    mydb, mycursor = connect_db.connect_database("metminidb")


    sql_query = """SELECT * FROM actual WHERE ts_epoch >= %s limit %s"""
    mycursor.execute(sql_query, (forecast_ts_utc,recs_to_retrieve,))
    records = mycursor.fetchall()

    for row in records:
        pressure_values.append(row[4])
        wind_deg_values.append(row[6])

    print(pressure_values)
    print(wind_deg_values)

    trend_str, slope = trend.trendline(index, pressure_values)
    wind_deg_avg = int(sum(wind_deg_values)) / len(wind_deg_values)
    wind_deg_avg = int(wind_deg_avg)

    pressure = pressure_values[0]   # use the first one
    ptrend = trend_str
    wind_quadrant = met_funcs.wind_deg_to_quadrant(wind_deg_avg)

    return pressure, ptrend, wind_quadrant


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


def sleep_forecast_time(utc_hour_required, utc_minute_required):
    """
    Sleep until 0900 UTC
    """
    sleep_period = 20

    while True:
        print('-----')
        now = time.time()
        utc_now = datetime.utcnow()
        print("Local time : " + time.ctime())
        #print(datetime.timestamp(utc_now))
        utc_hour   = utc_now.hour
        utc_minute = utc_now.minute
        utc_second = utc_now.second
        print("UTC hour   : " + utc_hour.__str__())
        print("UTC minute : " + utc_minute.__str__())
        print("UTC second : " + utc_second.__str__())

        if utc_hour >= utc_hour_required and utc_minute >= utc_minute_required:
            return

        msg = "Waiting for hour>=" + utc_hour_required.__str__() + ", minute>=" + utc_minute_required.__str__() + " ..."
        print(msg)
        time.sleep(sleep_period)

    return


def add_forecast_to_db(pressure, ptrend, wind_quadrant, forecast_text):
    """

    :param ressure:
    :param ptrend:
    :param wind_quadrant:
    :param forecast_text:
    :return:
    """
    utc_epoch = time.time()
    print("utc_epoch")

    mydb, mycursor = connect_db.connect_database("metminidb")

    ts_local = ts_funcs.epoch_to_local(utc_epoch)
    ts_utc   = ts_funcs.epoch_to_utc(utc_epoch)

    sql = "INSERT INTO forecasts (" \
          "ts_local, " \
          "ts_utc, " \
          "pressure, " \
          "ptrend, " \
          "wind_quadrant, " \
          "forecast" \
          ") " \
          "VALUES (%s, %s, %s, %s, %s, %s)"

    val = (ts_local,
           ts_utc,
           pressure,
           ptrend,
           wind_quadrant,
           forecast_text
           )

    print(sql)

    mycursor.execute(sql, val)
    mydb.commit()
    print(mycursor.rowcount, "record inserted in MySQL OK")

# ---------------------------------------------------


def main():
    forecast_hour_utc = 10      # FIXME : use 10 for now - run forecast algorithm at 09:00 UTC (so why is it not 9 ?)
    day_in_secs = 20 * 60 * 60

    while True:
        # 0930 UTC - and pull 3 x 10 min records =
        sleep_forecast_time(9, 30)    # time when the forecast is made and added to MySQL (9,30) = 0930 UTC = 1030 UK (in Summer)

        pressure, ptrend, wind_quadrant = get_forecast_prereqs(forecast_hour_utc)

        forecast_text = forecaster.get_forecaster_text(pressure, ptrend, wind_quadrant)
        full_forecast_txt = time.ctime() + "\n"
        full_forecast_txt += "Forecast for next 12 hours : " + forecast_text
        full_forecast_txt += "\n"
        full_forecast_txt+= "pressure=" + pressure.__str__() + " mbar (" + ptrend + "), wind=" + wind_quadrant

        print(full_forecast_txt)

        add_forecast_to_db(pressure, ptrend, wind_quadrant, forecast_text)

        print("sleep for 20 hours...")
        time.sleep(day_in_secs)


if __name__ == '__main__':
    main()
