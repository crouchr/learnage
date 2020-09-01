#!/usr/bin/python
# Sytel
# R.Crouch
# Listen for HTTP POST requests and create jobs in job file for revealManager.py to pick up and execute
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

import revealConfig
import revealFuncs
import revealJobId

_tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
application = Flask(__name__, template_folder=_tmpl_dir)

Version = "2.0.0"

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

@application.route("/ensight/v1.0/status", methods=['GET'])
def status():
    """Return a simple status message to be used by smoke tests, by pointing browser at http://127.0.0.1:5000/reveal/v1.0/status"""
    try:
        application.logger.info('Entered status()')

        return render_template('status.html', status="OK", server_time=time.ctime(), node=platform.node(),
                               version=Version)
    except Exception, e:
        print "status() : exception : " + e.__str__()
        return False


@application.route("/ensight/v1.0/statusjson", methods=['GET'])
def status_json():
    """Return a simple status message (in JSON format) to be used by smoke tests, by pointing browser at http://127.0.0.1:5000/reveal/v1.0/statusjson"""
    try:
        application.logger.info('Entered status_json()')

        response_json = {'status': 'OK', 'node': platform.node(), 'server_time': time.ctime(), 'version': Version}
        return jsonify(response_json)

    except Exception, e:
        print "status_json() : exception : " + e.__str__()
        return False


@application.route("/ensight/v1.0/doscan", methods=['POST'])
def do_scan():
    try:
        application.logger.info('Entered do_scan()')

        config_data = revealConfig.VerifyConfig()

        reveal_job_id = revealJobId.getJobId()  # Get the current value
        log_msg = "RevealFlaskApp : revealJobId = " + reveal_job_id.__str__()
        revealFuncs.doLog("NULL", log_msg)

        print "\n--------------------------------"
        print time.ctime()
        print "reveal_job_id : " + reveal_job_id.__str__()
        src_ip = request.remote_addr
        print "index() called"

        print "HTTP POST Request received by Flask server OK from source IP " + src_ip.__str__()
        print "reveal_job_id = " + reveal_job_id.__str__()
        pprint(request.form)  # ImmutableMultiDict

        # Mandatory fields - no need to check for existence
        print "[00] -> scenario    = " + request.form['scenario']

        domain = request.form['domain'].rstrip(" ")
        if not domain.isdigit():
            domain = domain.lower()
            # domain = domain.replace("as","")	# strip BGP ASN - was breaking domains containing "as" at MWC16
        if "." not in domain :
            revealFuncs.doLog(reveal_job_id,"domain field format error, domain=" + domain.__str__())
            return False
        print "[01] -> domain      = " + domain

        email = request.form['email'].rstrip(" ")
        print "[02] -> email       = " + email
        if "." not in email :
            revealFuncs.doLog(reveal_job_id,"email field format error, email=" + email.__str__())
            return False

        client = request.form['client'].rstrip(" ")
        print "[03] -> client      = " + client

        person = request.form['person'].rstrip(" ")
        print "[04] -> person      = " + person

        company = request.form['company'].rstrip(" ")
        print "[05] -> company     = " + company

        if request.form['country']:
            country = request.form['country'].rstrip(" ")
        else:
            country = "Unspecified"
        print "[06] -> country     = " + country

        if request.form['industry']:
            industry = request.form['industry'].rstrip(" ")
        else:
            industry = "Unspecified"
        print "[07] -> industry    = " + industry

        tag = request.form['tag'].rstrip(" ")
        print "[08] -> tag         = " + tag

        # Optional fields
        if 'nmap' in request.form:
            nmap = True
        else:
            nmap = False
        print "[09] -> nmap        = " + nmap.__str__()

        if 'ccemail' in request.form:
            ccemail = request.form['ccemail'].rstrip(" ")
            if len(ccemail) >= 1 and "." not in ccemail:
                revealFuncs.doLog(reveal_job_id, "RevealFlaskApp : ccemail field format error, ccemail=" + ccemail.__str__())
                return False
        else:
            ccemail = "NONE"
        if ccemail == "":
            ccemail = "NONE"
        print "[10] -> ccemail     = " + ccemail.__str__()

        if 'dnsenum' in request.form:
            revealFuncs.doLog(reveal_job_id, "dnsenum = " + request.form['dnsenum'].__str__())
            if request.form['dnsenum'].upper() == "TRUE":
                dnsenum = True
            else:
                dnsenum = False
        else:
            dnsenum = False
        revealFuncs.doLog(reveal_job_id, "[11] dnsenum = " + dnsenum.__str__())

        if 'comply' in request.form:
            revealFuncs.doLog(reveal_job_id, "comply = " + request.form['comply'].__str__())
            if request.form['comply'].upper() == "TRUE":
                comply = True
            else:
                comply = False
        else:
            comply = False
        print "[12] -> comply      = " + comply.__str__()

        if 'cryptpin' in request.form:
            cryptpin = request.form['cryptpin']
            if len(cryptpin) < 6 or len(cryptpin) > 16:
                cryptpin = request.form['cryptpin'].rstrip(" ")  # encrypt the sensitive files in the email
                revealFuncs.doLog(reveal_job_id, "cryptpin field format error, cryptpin=" + cryptpin.__str__())
                return False
        else:
            cryptpin = "NONE"
        if cryptpin == "":
            cryptpin = "NONE"
        print "[13] -> cryptpin    = " + cryptpin.__str__()

        if 'debug' in request.form:
            revealFuncs.doLog(reveal_job_id, "debug = " + request.form['debug'].__str__())
            if request.form['debug'].upper() == "TRUE":
                debug = True
            else:
                debug = False
        else :
            debug = False
        revealFuncs.doLog(reveal_job_id, "[14] debug = " + debug.__str__())

        if 'emailownage' in request.form:
            revealFuncs.doLog(reveal_job_id,"email0wnage = " + request.form['emailownage'].__str__())
            if request.form['emailownage'].upper() == "TRUE" :
                emailownage = True
            else:
                emailownage = False
        else:
            emailownage = False
        revealFuncs.doLog(reveal_job_id, "[15] -> emailownage = " + emailownage.__str__())

        if 'subdomains' in request.form:
            revealFuncs.doLog(reveal_job_id, "subdomains = " + request.form['subdomains'].__str__())
            if request.form['subdomains'].upper() == "TRUE":
                subdomains = True
            else:
                subdomains = False
        else:
            subdomains = False
        revealFuncs.doLog(reveal_job_id, "[16] -> subdomains = " + subdomains.__str__())

        if 'vulns' in request.form:
            revealFuncs.doLog(reveal_job_id, "vulns = " + request.form['vulns'].__str__())
            if request.form['vulns'].upper() == "TRUE" :
                vulns = True
            else:
                vulns = False
        else:
            vulns = False
        revealFuncs.doLog(reveal_job_id, "[17] -> vulns = " + vulns.__str__())

        if 'allhosts' in request.form:
            revealFuncs.doLog(reveal_job_id, "allhosts = " + request.form['allhosts'].__str__())
            if request.form['allhosts'].upper() == "TRUE":
                allhosts = True
            else:
                allhosts = False
        else:
            allhosts = False
        print "[18] -> allhosts    = " + allhosts.__str__()

        # obsolete - refactor this variabel out at some point
        if 'mwc' in request.form:
            mwc = True
        else:
            mwc = False
        print "[99] -> mwc         = " + mwc.__str__()

        print "--------------"

        # We only want a domain, not a hostname...
        # fixme : make this a function so it can be unittested
        domain = domain.replace("www.", "")
        domain = domain.replace("https://", "")
        domain = domain.replace("http://", "")

        # fixme : need to sanitise input values
        job = {}

        # sanitise strings
        job['domain'] = sanitise(domain)  # domain to scan e.g. ox.ac.uk or BGP ASN
        job['client'] = sanitise(client)  # name of software using the API
        job['email'] = sanitise(email)  # email address to receive the assessment Report
        job['person'] = sanitise(person)  # person requesting the Assessment
        job['company'] = sanitise(company)  # Name of Company that Person represents
        job['ccemail'] = sanitise(ccemail)  #
        job['cryptpin'] = sanitise(cryptpin)
        job['country']  = sanitise(country)
        job['industry'] = sanitise(industry)
        job['tag'] = sanitise(tag)

        # do not santise booleans
        job['emailownage'] = emailownage
        job['comply']      = comply
        job['allhosts']    = allhosts
        job['dnsenum']     = dnsenum
        job['vulns']       = vulns

        # job['subdomains']  = subdomains
        job['subdomains'] = False  # disable this for MWC16 and consider if it is really needed

        # job['nmap']        = nmap
        job['nmap'] = False

        # job['debug']       = debug
        job['debug'] = False

        job['vulns'] = False    # todo : functionality is a work in progress so override until backend is working

        if job['domain'].isdigit():
            job['action'] = "SCAN_ASN"  # SCAN = perform assessment of target domain DELETE = abort assessment of target
        else:
            job['action'] = "SCAN_DOMAIN"  # SCAN = perform assessment of target domain DELETE = abort assessment of target

        pprint(job)

        if "SCAN" in job['action']:
            #reveal_job_id = g.reveal_job.getAndIncrement()
            reveal_job_id = revealJobId.getAndIncrementJobId()  # Get the current value

        if platform.system() == "Linux":
            job_filename = config_data.values['dirs']['verify_base'] + "/var/log/" + "jobfile.csv"
        else:
            job_filename = "jobfile.csv"  # fixme : add Windows directory delimiters

        job_rec = time.ctime() + "," + job['action'] + "," + reveal_job_id.__str__() + "," + job[
            'client'].__str__() + "," + \
                  job['company'].__str__() + "," + job['person'].__str__() + "," + job['email'].__str__() + "," + job[
                      'ccemail'].__str__() + "," + \
                  job['domain'].__str__() + "," + job['nmap'].__str__() + "," + job['dnsenum'].__str__() + "," + job[
                      'cryptpin'].__str__() + "," + \
                  job['debug'].__str__() + "," + job['emailownage'].__str__() + "," + job[
                      'subdomains'].__str__() + "," + job['vulns'].__str__() + "," + \
                  job['allhosts'].__str__() + "," + job['country'].__str__() + "," + job['industry'].__str__() + "," + \
                  job['comply'].__str__() + "," + job['tag'].__str__()

        revealFuncs.doLog(reveal_job_id, "RevealFlaskApp : Appending job_rec to " + job_filename + " : " + job_rec)

        fpOut = open(job_filename, "a")
        print >> fpOut, job_rec
        fpOut.flush()
        fpOut.close()

        # fixme : make this more HTTP like ?
        response = reveal_job_id.__str__()

        revealFuncs.doLog("NULL", "response is : " + response.__str__())

        return response

    except Exception, e:
        log_msg = "RevealFlask/app.py : doscan() : exception : " + e.__str__()
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
