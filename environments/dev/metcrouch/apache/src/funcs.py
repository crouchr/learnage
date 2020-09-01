#!/usr/bin/python

# (C) 2015 Sytel-Reply 

# Standard Python modules
import glob
import syslog
import os
import subprocess32 as subprocess
import re
import time
import urllib
import urllib2

from IPy import IP
from pprint import pprint
from threading import Timer

import revealConfig

#################################################################################
# Log tracebacks : fixme - make this a re-usable function and add to verify.ini ?
import logging

logging.basicConfig(filename="/tmp/verify-traceback.log", level=logging.DEBUG, format='%(asctime)s - %(message)s')
#################################################################################

# fixme : move this to a unit test
def test_once():
    '''Test traceback logging'''
    try :
        a = 1/0
    except :
        logging.exception("Something bad in test_once()")
        raise


def get_verify_env():
    '''
    Return the value of the REVEAL environment variable
    :return:
    '''
    os_env_dict = os.environ
    if os_env_dict.has_key('REVEAL'):
        environment_type = os_env_dict['REVEAL']
    else:
        environment_type = "UNKNOWN"

    return environment_type.__str__()

# include all scripts that are not daemons nor controlled by cron
def map_cmd(env_str,cmdStr):
    try :

        command_mapper = {
        'reveal0wnageEmailExe'  : 'Reveal0wnageEmailApp/src/Reveal0wnageEmail/app.py',
        'revealDnsDumpsterExe'  : 'RevealDnsDumpsterApp/src/RevealDnsDumpster/app.py',
        'revealEmailResultsExe' : 'RevealEmailResultsApp/src/RevealEmailResults/app.py',
        'revealHtmlReporterExe' : 'RevealHtmlReporterApp/src/RevealHtmlReporter/app.py',
        'revealMainExe'         : 'RevealMainApp/src/RevealMain/app.py',
        'revealNetReportExe'    : 'RevealNetReportApp/src/RevealNetReport/app.py',
        'revealPunterExe'       : 'RevealPunterApp/src/RevealPunter/app.py',
        'revealReconNGExe'      : 'RevealReconNGApp/src/RevealReconNG/app.py',
        'revealShodanScanExe'   : 'RevealShodanScanApp/src/RevealShodanScan/app.py',
        'revealWorkerExe'       : 'RevealWorkerApp/src/RevealWorker/app.py'
        }

        if env_str == 'DEV' :
            cmd_name = cmdStr.split(" ")[0]  # e.g. reveal0wnageEmailExe
            if command_mapper.has_key(cmd_name):
                cmd_name_dev = '/home/coder/PycharmProjects/reveal-verify/backend/src/' + command_mapper[cmd_name]
                cmdStr = cmdStr.replace(cmd_name, cmd_name_dev)

        return cmdStr

    except Exception, e:
        log_msg = "revealFuncs.py : map_cmd() : exception : " + e.__str__() + ", env_str=" + env_str.__str__() + ", cmdStr=" + cmdStr.__str__()
        doLog("NULL",log_msg)
        logging.exception("Exception")
        return None

def runCmd(jobId, cmd_str_list, background = False, timeout_secs=300):
    '''
    Run cmdStr in foreground
    :param jobId:
    :param cmd_str_list:
    :return:
    '''

    try:

        cmd_str_list_normalised = []

        kill = lambda process: process.kill()

        for i in cmd_str_list :
            if i != '' :
                if isinstance(i,basestring):
                    i = i.lstrip(" ")   # strip any leading spaces
                cmd_str_list_normalised.append(i)

        env_type = get_verify_env()

        cmd_str_list[0] = map_cmd(env_type, cmd_str_list_normalised[0])

        log_msg = "revealFuncs.py : runCmd() : cmd_str_list_normalised=" + cmd_str_list_normalised.__str__() + ", timeout_secs=" + timeout_secs.__str__() + ", background=" + background.__str__()
        doLog(jobId, log_msg)

        #cmdStr = map_cmd(env_type, cmd_str_list_normalised)
        #cmdStr = cmdStr + " &" # run in background
        #proc = subprocess.Popen(cmdStr, shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
        #proc = subprocess32.runcall(cmd_str_list_normalised, stdout=subprocess.PIPE)
        #subprocess.run(cmd_str_list_normalised)

        start_time = time.time()
        my_timer = Timer(timeout_secs, kill, cmd_str_list[0])

        proc = subprocess.Popen(cmd_str_list_normalised, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=-1)

        try :
            my_timer.start()
            stdout, stderr = proc.communicate()
        finally :
            my_timer.cancel()

        if background != True:
            log_msg = "revealFuncs.py : runCmd() : now wait until foreground subprocess has completed..."
            doLog(jobId, log_msg)
            proc.wait()     # wait until called script has completed

        stop_time = time.time()

        log_msg = "revealFuncs.py : runCmd() : subprocess COMPLETED and took " + (stop_time - start_time).__str__() + " seconds to run"
        doLog(jobId, log_msg)

        #subprocess.call(cmd_str_list_normalised)
        #pipe = os.popen(cmdStr,'r')
        #pipe.read()

        return True

    except Exception, e:
        log_msg = "revealFuncs.py : runCmd() : exception : " + e.__str__() + ", cmd_str_list_normalised=" + cmd_str_list_normalised.__str__()
        doLog("NULL", log_msg)
        logging.exception("Exception")
        return None

def doLog(jobId, msg):
    pid = os.getpid()
    if jobId == "NULL" :
        log_msg = msg.__str__()
    else:
        log_msg = "jobId=" + jobId.__str__() + " : " + msg.__str__()

    log_msg = "pid=" + pid.__str__() + " => " + log_msg
    print time.ctime() + " : " + log_msg.__str__()
    syslog.syslog(log_msg.__str__())

def jdefault(o):
    '''
    Allow this object to be JSONable
    '''
    return o.__dict__

def union(a, b):
    """ return the union of two lists """
    return list(set(a) | set(b))

def stripNonAscii(string):
    '''
    Returns the string with non-ASCII stripped
    '''
    stripped = (c for c in string if 0 < ord(c) < 127)
    result = ''.join(stripped)
    return result

def submitTestJob(company, domain, tag, recipient_email, recipient_person, scenario, comply, vulns, client):
    '''
    Submit a Reveal Verify Report Request via POST API
    '''
    try:

        port = int(revealConfig.VerifyConfig().values['flask']['port'])
        url = "http://127.0.0.1:" + port.__str__() + "/reveal/v1.0/doscan"
        print url

        values = {"client"      : client,   # e.g. name of executable
                  "email"       : recipient_email,
                  "person"      : recipient_person,
                  "company"     : company,
                  "country"     : "unspecified",
                  "industry"    : "unspecified",
                  "cryptpin"    : "123456",
                  "tag"         : tag,
                  "scenario"    : scenario,
                  "dnsenum"     : "TRUE",
                  "subdomains"  : "FALSE",
                  "regtoken"    : "T33333",
                  "comply"      : comply,           #"FALSE",
                  "vulns"       : vulns,            #"FALSE",
                  "emailownage" : "FALSE",
                  "allhosts"    : "FALSE",
                  "domain"      : domain
                  }


        print "------------------------------------------"
        print time.ctime()
        pprint(values)

        data = urllib.urlencode(values)

        # Send the request
        req = urllib2.Request(url, data)

        # Receive the response = jobId
        response = urllib2.urlopen(req)
        the_page = response.read()

        # print the_page.__str__()

        return the_page

    except Exception, e:
        log_msg = "submit() : exception : " + e.__str__()
        doLog("NULL",log_msg)
        logging.exception("Exception")
        return None



# dump system paths to file
def dump_environment():
    os_env_dict = os.environ
    for i in os_env_dict:
        if i in ['PYTHONPATH','HOME','USER','LOGNAME','PATH']:
            log_msg = i + " -> " + os_env_dict[i].__str__()
            doLog("NULL", log_msg)

def is_ipv4_public(ip):
    ips = re.findall('\d+\.\d+\.\d+\.\d+', ip)
    if len(ips) != 1:
        return False
    ipObj = IP(ip)
    address_type = ipObj.iptype()
    if address_type is not 'PRIVATE':
        return True
    else:
        return False

# fixme : incorprate directory from revealConfig
def storepid(pid_directory,tag):
    """
    Get pid and write to file
    tag is the first part of the .pid file (e.g. apache2)
    :param tag:
    :return:
    """
    pid = os.getpid()
    pid_filename = pid_directory + '/' + tag + ".pid"

    fp_out = open(pid_filename,'w')
    print >> fp_out,pid.__str__()
    fp_out.close()

    doLog("NULL","Wrote pid to pidfile : " + pid_filename.__str__())

    return pid_filename




# e.g. domain = reply or jagex
def getFierceResultsFilenames(directory, domain):
    '''
    Return a list of fierce.pl results files that match the word 'domain'
    '''
    filenameList = []

    # print "Change directory to : " + directory + " and glob for " + domain
    os.chdir(directory)
    for filename in glob.glob("fierce_results_" + domain.upper() + "*"):
        if "~" in filename:
            continue  # do not want to process backup files
        filenameList.append(filename)

    return filenameList


# e.g. target = JAGEX
def getProcessedFierceResultsFilenames(directory, target):
    '''
    Return a list of fierce.pl results files that match the word 'target'
    '''
    filenameList = []

    # print "Change directory to : " + directory + " and glob for " + target
    os.chdir(directory)
    for filename in glob.glob("*" + target.upper() + ".hosts.tsv"):
        if "~" in filename:
            continue  # do not want to process backup files
        filenameList.append(filename)

    return filenameList


def getKnockpyResultsFilenames(directory, domain):
    '''
    Return a list of knockpy results files that match the word 'domain'
    '''
    filenameList = []
    os.chdir(directory)
    for filename in glob.glob("knockpy_results_" + domain.upper() + "*"):
        if "~" in filename:
            continue  # do not want to process backup files
        filenameList.append(filename)

    return filenameList


# e.g. target = JAGEX or target = JOB-999
def getProcessedKnockpyResultsFilenames(directory, target):
    '''
    Return a list of knockpy results files that match the word 'target'
    '''
    filenameList = []
    os.chdir(directory)
    for filename in glob.glob("verify-" + target.upper() + ".hosts.tsv"):
        if "~" in filename:
            continue  # do not want to process backup files
        filenameList.append(filename)

    return filenameList


# IP is a.b.c.d
def calcSlash24(ip):
    '''
    Calculate /24 route from CIDR route
    '''
    if ip == "":
        return None

    if type(ip) != str:
        return None

    a = ip.split(".")
    if len(a) != 4:
        return None

    route = a[0] + "." + a[1] + "." + a[2] + ".0/24"
    return route


def whereAmI():
    '''Display where this file is stored'''
    current_dir = os.path.abspath(os.path.dirname(__file__))
    print current_dir
    return current_dir


def isValidIpv4(ip):
    '''
    Return True if IPv4 addess is valid else return False
    '''
    try:
        if ip == None:
            return False

        if "." not in ip:
            return False

        octets = ip.split(".")
        if len(octets) != 4:
            return False
        for octet in octets:
            val = int(octet)  # e.g. 128
            if (val <= 0) or (val >= 256):
                return False

        # IP is valid        
        return True

    except Exception, e:
        print "isValidIpv4() : exception : " + e.__str__() + ", for ip=" + ip.__str__()
        logging.exception("Exception")
        return False


###########################    
# T E S T  H A R N E S S  #
###########################    
if __name__ == '__main__':


    #ipList = ["0.0.0.0", "1.1.1.1", None, "", "255.255.255.255", "10.2.3.4", "10.2.3.256"]
    #for ip in ipList:
    #    result = isValidIpv4(ip)
    #    print "ip=" + ip.__str__() + " -> " + result.__str__()
    #
    #    dump_environment()

    #test_once()

    map_cmd("junk","DEV")