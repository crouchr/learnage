#!/usr/bin/python
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

    except Exception, e:
        print "status_json() : exception : " + e.__str__()
        return False


@application.route("/getmetinfo", methods=['POST'])
def getmetinfo():
    """
    Perform logging of met data to SQL database
    :return:
    """
    try:
        application.logger.info('Entered getmetinfo()')

        config_data = config.VerifyConfig()
        utc = datetime.utcnow()
        print "\n--------------------------------"
        print time.ctime()
        print "UTC : " + utc.__str__()

        src_ip = request.remote_addr
        print "getmetinfo() called"

        print "HTTP POST Request received by Flask server OK from source IP " + src_ip.__str__()
        pprint(request.form)  # ImmutableMultiDict

        # Mandatory fields - no need to check for existence
        #print "[00] -> scenario  = " + request.form['scenario']

        pressure = int(request.form['pressure'].rstrip(" "))
        print "[01] -> pressure  = " + pressure.__str__()

        ptrend = request.form['ptrend'].rstrip(" ")
        print "[02] -> ptrend    = " + ptrend

        wind_dir = request.form['wind_dir'].rstrip(" ")
        print "[03] -> wind_dir  = " + wind_dir

        bforecast = request.form['bforecast'].rstrip(" ")
        print "[04] -> bforecast = " + bforecast

        clouds = request.form['clouds'].rstrip(" ")
        print "[05] -> clouds    = " + clouds

        yest_rain = request.form['yest_rain'].rstrip(" ")
        print "[06] -> yest_rain = " + yest_rain.__str__()

        yest_wind = request.form['yest_wind'].rstrip(" ")
        print "[07] -> yest_wind = " + yest_wind.__str__()

        yest_min_temp = request.form['yest_min_temp'].rstrip(" ")
        print "[08] -> yest_min_temp = " + yest_min_temp.__str__()

        yest_max_temp = request.form['yest_max_temp'].rstrip(" ")
        print "[09] -> yest_max_temp = " + yest_max_temp.__str__()

        location = request.form['location'].rstrip(" ")
        print "[10] -> location  = " + location.__str__()

        notes = request.form['notes'].rstrip(" ")
        print "[11] -> notes     = " + notes.__str__()

        email = request.form['email'].rstrip(" ")
        print "[12] -> email     = " + email.__str__()

        #client = request.form['client'].rstrip(" ")
        #print "[03] -> client      = " + client

        print "--------------"

        job = {}
        job['pressure'] = pressure

        pprint(job)

        #job_rec = time.ctime() + "," + job['action'] + "," + reveal_job_id.__str__() + "," + job[
        #    'client'].__str__() + "," + \
        #          job['company'].__str__() + "," + job['person'].__str__() + "," + job['email'].__str__() + "," + job[
        #              'ccemail'].__str__() + "," + \
        #          job['domain'].__str__() + "," + job['nmap'].__str__() + "," + job['dnsenum'].__str__() + "," + job[
        #              'cryptpin'].__str__() + "," + \
        #          job['debug'].__str__() + "," + job['emailownage'].__str__() + "," + job[
        #              'subdomains'].__str__() + "," + job['vulns'].__str__() + "," + \
        #          job['allhosts'].__str__() + "," + job['country'].__str__() + "," + job['industry'].__str__() + "," + \
        #          job['comply'].__str__() + "," + job['tag'].__str__()

        #funcs.doLog(reveal_job_id, "RevealFlaskApp : Appending job_rec to " + job_filename + " : " + job_rec)

        #fpOut = open(job_filename, "a")
        #print >> fpOut, job_rec
        #fpOut.flush()
        #fpOut.close()

        # fixme : make this more HTTP like ?
        #response = reveal_job_id.__str__()

        #revealFuncs.doLog("NULL", "response is : " + response.__str__())
        response = "OK"
        return response

    except Exception, e:
        log_msg = "app.py : getmetinfo() : exception : " + e.__str__()
        funcs.doLog("NULL", log_msg)
        return False


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    log_msg = "Started, version=" + version
    funcs.doLog("NULL", log_msg)
    app_log_file  = "/var/log/minimet.log"
    app_log_file = "/tmp/minimet.log"

    config_data = config.VerifyConfig()

    flask_ip = config_data.values['flask']['ip']
    flask_port = int(config_data.values['flask']['port'])

    # Store this process pid in a file to be monitored by monit
    #revealFuncs.storepid('/opt/reveal-verify/backend/var/run','revealflask')

    # Create object
    #reveal_job = revealPersist.Persist(config_data.values['dirs']['verify_base'] + "/var/run/" + "jobid-persist.txt", job_id_start, 1, "")
    #g.reveal_job = reveal_job

    print "flask_ip     : " + flask_ip
    print "flask_port   : " + flask_port.__str__()

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

    DEBUG = False
    application.run(debug=DEBUG, host=flask_ip, port=flask_port, use_reloader=False)


if __name__ == '__main__':
    main()
