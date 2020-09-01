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

from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request

import minimetconfig

_tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
application = Flask(__name__, template_folder=_tmpl_dir)

Version = "1.0.0"


def harness():
    """This function purely exists to be run from unit test harness"""
    return "OK"


def sanitise(x):
    '''
    Basic sanitisation of input entered by web-user
    '''
    if x is None:
        return None
    x = x.replace(",", "")  # replace ","
    x = x.rstrip(" ")  # strip trailing spaces
    x = x.lstrip(" ")  # strip leading spaces
    x = x.replace("\t", "")  # strip TAB characters

    return x


@application.errorhandler(500)
def internal_err(exception):
    application.logger.error(exception)
    return render_template('500.html'),500

@application.route("/status", methods=['GET'])
def status():
    """Return a simple status message to be used by smoke tests, by pointing browser at http://127.0.0.1:5000/reveal/v1.0/status"""
    try:
        application.logger.info('Entered status()')

        return render_template('status.html', status="OK", server_time=time.ctime(), node=platform.node(),
                               version=Version)
    except Exception, e:
        print "status() : exception : " + e.__str__()
        return False


@application.route("/statusjson", methods=['GET'])
def status_json():
    """Return a simple status message (in JSON format) to be used by smoke tests, by pointing browser at http://127.0.0.1:5000/reveal/v1.0/statusjson"""
    try:
        application.logger.info('Entered status_json()')

        response_json = {'status': 'OK', 'node': platform.node(), 'server_time': time.ctime(), 'version': Version}
        return jsonify(response_json)

    except Exception, e:
        print "status_json() : exception : " + e.__str__()
        return False


@application.route("/dolog", methods=['POST'])
def do_log():
    """
    Perform logging of met data to SQL database
    :return:
    """
    try:
        application.logger.info('Entered do_log()')

        config_data = minimetconfig.VerifyConfig()

        print "\n--------------------------------"
        print time.ctime()
        src_ip = request.remote_addr
        print "do_log() called"

        print "HTTP POST Request received by Flask server OK from source IP " + src_ip.__str__()
        pprint(request.form)  # ImmutableMultiDict

        # Mandatory fields - no need to check for existence
        print "[00] -> scenario    = " + request.form['scenario']

        pressure = int(request.form['pressure'].rstrip(" "))
        print "[01] -> pressure      = " + pressure

        #client = request.form['client'].rstrip(" ")
        #print "[03] -> client      = " + client

        print "--------------"


        # fixme : need to sanitise input values
        job = {}

        # sanitise strings
        job['pressure'] = pressure

        pprint(job)

        if "SCAN" in job['action']:
            #reveal_job_id = g.reveal_job.getAndIncrement()
            reveal_job_id = revealJobId.getAndIncrementJobId()  # Get the current value

        if platform.system() == "Linux":
            job_filename = config_data.values['dirs']['verify_base'] + "/var/log/" + "jobfile.csv"
        else:
            job_filename = "jobfile.csv"  # fixme : add Windows directory delimiters

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

        #revealFuncs.doLog(reveal_job_id, "RevealFlaskApp : Appending job_rec to " + job_filename + " : " + job_rec)

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
        log_msg = "app.py : do_log() : exception : " + e.__str__()
        revealFuncs.doLog("NULL", log_msg)
        return False

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    log_msg = "Started, version=" + Version
    revealFuncs.doLog("NULL", log_msg)
    app_log_file  = "/var/log/verify-flask.log"

    config_data = revealConfig.VerifyConfig()

    flask_ip = config_data.values['flask']['ip']
    flask_port = int(config_data.values['flask']['port'])

    # Store this process pid in a file to be monitored by monit
    revealFuncs.storepid('/opt/reveal-verify/backend/var/run','revealflask')

    #ctx = application.app_context()
    #ctx.push()

    job_id_start = 20000

    # Create object
    #reveal_job = revealPersist.Persist(config_data.values['dirs']['verify_base'] + "/var/run/" + "jobid-persist.txt", job_id_start, 1, "")
    #g.reveal_job = reveal_job
    revealJobId.createJobIdFile(initialValue=job_id_start)

    print "flask_ip     : " + flask_ip
    print "flask_port   : " + flask_port.__str__()
    print "job_id_start : " + job_id_start.__str__()

    # Setup a logger that Flask will use
    handler = RotatingFileHandler(app_log_file, maxBytes=100000, backupCount=1)
    handler.setLevel(logging.DEBUG)     # was INFO
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(funcName)s - %(message)s in source file %(pathname)s")
    handler.setFormatter(formatter)

    application.logger.addHandler(handler)
    getLogger('werkzeug').addHandler(handler)

    log_msg = "RevealFlaskApp version " + Version + " listening for HTTP POST requests on " + flask_ip.__str__() + " on port " + flask_port.__str__()
    revealFuncs.doLog("NULL", log_msg)

    revealFuncs.doLog("NULL", "Flask logging to : " + app_log_file)

    DEBUG = False
    application.run(debug=DEBUG, host=flask_ip, port=flask_port, use_reloader=False)

if __name__ == '__main__':
    main()
