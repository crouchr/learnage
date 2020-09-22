#!/usr/bin/python3
# R.Crouch
# Listen for HTTP POST requests
#
# To do :
# [1] Add encryption between PHP server and this flask server
# [2] Add authentication between PHP server and this flask server
# [3] Add syslog
#
# fixme :
# Need to be able to pass back an error message to the web user

# Standard modules
import platform
import sys
import time
import logging
import os
import traceback

from pprint import pprint
from logging.handlers import RotatingFileHandler
from logging import getLogger
from datetime import datetime
from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request

# minimet modules
import config
import funcs
import forecaster
import data_logging # logging to TSV file
import connect_db
import met_funcs

_tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
application = Flask(__name__, template_folder=_tmpl_dir)

version = "1.0.0"


def harness():
    """
    This function purely exists to be run from unit test harness
    """
    return "OK"


@application.errorhandler(500)
def internal_err(exception):
    application.logger.error(exception)
    return render_template('500.html'),500

#@application.route("/status", methods=['GET'])
#def status():
#    """Return a simple status message to be used by smoke tests, by pointing browser at http://127.0.0.1:5000/reveal/v1.0/status"""
#    try:
#        application.logger.info('Entered status()')
#
#        return render_template('status.html',
#                               status="OK",
#                               server_time=time.ctime(),
#                               node=platform.node(),
#                               version=version)
#    except Exception, e:
#        print "status() : exception : " + e.__str__()
#        return False


@application.route("/statusjson", methods=['GET'])
def status_json():
    """Return a simple status message (in JSON format) to be used by smoke tests, by pointing browser at http://127.0.0.1:5000/reveal/v1.0/statusjson"""
    try:
        application.logger.info('Entered status_json()')

        response_json = {'status': 'OK', 'node': platform.node(), 'server_time': time.ctime(), 'version': version}
        return jsonify(response_json)

    except Exception as e:
        print("status_json() : exception : " + e.__str__())
        return False


@application.route("/getmetinfo", methods=['POST'])
def getmetinfo():
    """
    Perform logging of met data to SQL database
    :return:
    """
    try:
        application.logger.info('Entered getmetinfo()')
        met_data_log_filename = "/tmp/metmini_data.tsv"

        config_data = config.VerifyConfig()
        print("\n--------------------------------")
        print(time.ctime())

        src_ip = request.remote_addr
        print("getmetinfo() called")

        print("HTTP POST Request received by Flask server OK from source IP " + src_ip.__str__())
        pprint(request.form)  # ImmutableMultiDict

        # Mandatory fields - no need to check for existence
        #print "[00] -> scenario  = " + request.form['scenario']

        pressure = int(request.form['pressure'].rstrip(" "))
        print("[01] -> pressure      = " + pressure.__str__())

        ptrend = request.form['ptrend'].rstrip(" ")
        print("[02] -> ptrend        = " + ptrend)

        wind_quadrant = met_funcs.request.form['wind_dir'].rstrip(" ")
        print("[03] -> wind_quadrant      = " + wind_quadrant)

        wind_strength = request.form['wind_strength'].rstrip(" ")
        print("[04] -> wind_strength = " + wind_strength)

        bforecast = request.form['bforecast'].rstrip(" ")
        print("[05] -> bforecast = " + bforecast)

        oforecast = request.form['oforecast'].rstrip(" ")
        print("[06] -> oforecast = " + oforecast)

        clouds = request.form['clouds'].rstrip(" ")
        print("[07] -> clouds    = " + clouds)

        coverage = request.form['coverage'].rstrip(" ")
        print("[08] -> coverage  = " + coverage)

        location = request.form['location'].rstrip(" ")
        print("[09] -> location  = " + location.__str__())

        notes = request.form['notes'].rstrip(" ")
        print("[10] -> notes     = " + notes.__str__())

        yest_rain = request.form['yest_rain'].rstrip(" ")
        print("[11] -> yest_rain = " + yest_rain.__str__())

        yest_wind = request.form['yest_wind'].rstrip(" ")
        print("[12] -> yest_wind = " + yest_wind.__str__())

        yest_min_temp = request.form['yest_min_temp'].rstrip(" ")
        print("[13] -> yest_min_temp = " + yest_min_temp.__str__())

        yest_max_temp = request.form['yest_max_temp'].rstrip(" ")
        print("[14] -> yest_max_temp = " + yest_max_temp.__str__())

        yest_notes = request.form['yest_notes'].rstrip(" ")
        print("[15] -> yest_notes    = " + yest_notes.__str__())

        email = request.form['email'].rstrip(" ")
        print("[16] -> email         = " + email.__str__())

        # only needed during development phase
        data_type = request.form['data_type'].rstrip(" ")
        print("[*]  -> data_type     = " + data_type.__str__())

        print("--------------")

        # Make forecast
        forecast_text = forecaster.get_forecaster_text(pressure, ptrend, wind_dir)

        metmini_data = {}
        metmini_data['pressure'] = pressure
        metmini_data['ptrend'] = ptrend
        metmini_data['wind_quadrant'] = wind_quadrant
        metmini_data['wind_strength'] = wind_strength
        metmini_data['forecast'] = forecast_text
        metmini_data['bforecast'] = bforecast
        metmini_data['oforecast'] = oforecast
        metmini_data['clouds'] = clouds
        metmini_data['coverage'] = coverage
        metmini_data['location'] = location
        metmini_data['notes'] = notes
        metmini_data['yest_rain'] = yest_rain
        metmini_data['yest_wind'] = yest_wind
        metmini_data['yest_min_temp'] = yest_min_temp
        metmini_data['yest_max_temp'] = yest_max_temp
        metmini_data['yest_notes'] = yest_notes
        metmini_data['data_type'] = data_type

        pprint(metmini_data)

        utc       = datetime.utcnow()
        localtime = datetime.now()

        # log to TSV - FIXME : this needs updating to reflect MySQL
        #data_logging.log_metmini_data_tsv(utc, metmini_data)

        # log to SQL
        ts_local = localtime.strftime('%Y-%m-%d %H:%M:%S')
        ts_utc   = utc.strftime('%Y-%m-%d %H:%M:%S')

        mydb, mycursor = connect_db.connect_database("metminidb")

        sql = "INSERT INTO metminilogs (" \
              "ts_local, " \
              "ts_utc," \
              "pressure, " \
              "ptrend, " \
              "wind_quadrant, " \
              "wind_strength, " \
              "forecast, " \
              "bforecast, " \
              "oforecast, " \
              "coverage, " \
              "location, " \
              "yest_rain, " \
              "yest_wind, " \
              "yest_min_temp, " \
              "yest_max_temp, " \
              "data_type) " \
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        val = (ts_local, ts_utc,
               pressure,
               ptrend,
               wind_quadrant,
               wind_strength,
               forecast_text,
               bforecast,
               oforecast,
               coverage,
               location,
               yest_rain,
               yest_wind,
               yest_min_temp,
               yest_max_temp,
               data_type)

        mycursor.execute(sql, val)
        mydb.commit()
        print(mycursor.rowcount, "record inserted in MySQL OK")

        response = forecast_text
        return response

    except Exception as e:
        log_msg = "EXCEPTION !!! : app.py : getmetinfo() : exception : " + e.__str__()
        funcs.doLog("NULL", log_msg)
        return False


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    print("Started")
    log_msg = "Started, version=" + version
    funcs.doLog("NULL", log_msg)
    app_log_file  = "/var/log/minimet.log"
    app_log_file = "/tmp/minimet.log"

    config_data = config.VerifyConfig()

    #flask_ip = config_data.values['flask']['ip']
    flask_port = int(config_data.values['flask']['port'])

    flask_port = 5001
    flask_ip = 'erminserver.localdomain'    # not using IP as there is a bug in Python 3.6

    print("flask_ip     : " + flask_ip)
    print("flask_port   : " + flask_port.__str__())

    # Setup a logger that Flask will use
    handler = RotatingFileHandler(app_log_file, maxBytes=100000, backupCount=1)
    handler.setLevel(logging.DEBUG)     # was INFO
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(funcName)s - %(message)s in source file %(pathname)s")
    handler.setFormatter(formatter)

    application.logger.addHandler(handler)
    getLogger('werkzeug').addHandler(handler)

    log_msg = "minimet version " + version + " listening for HTTP POST requests on " + flask_ip.__str__() + " on port " + flask_port.__str__()
    funcs.doLog("NULL", log_msg)

    funcs.doLog("NULL", "Flask logging to : " + app_log_file)

    mydb, mycursor = connect_db.connect_database()

    DEBUG = True
    application.run(debug=DEBUG, host=flask_ip, port=flask_port, use_reloader=False)


if __name__ == '__main__':
    main()
