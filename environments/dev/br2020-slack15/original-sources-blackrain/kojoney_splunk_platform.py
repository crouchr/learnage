#!/usr/bin/python

# Tail the /var/log/messages file and send data to SplunkCloud LaaS

import sys, time, os , syslog , urlparse , re 
import kojoney_loggly
import kojoney_splunk

import ipintellib	# RCH library - master on mars
import mailalert	# RCH library
import p0fcmd		# RCH library - master on mars
#import rch_asn_funcs	# RCH library - master on mars

# SplunkCloud credentials for 'Platform' Project
ACCESS_TOKEN = 'bhCSxrbWx9tRwoycO-Jf1Dh-KDBUQ01c_BbrTsPfaJVtRzvPdOT8JgKcKnuEjQYZLt5MZs1YKxM='
PROJECT_ID   = '801e1f44176a11e49e1c22000a9e07fe'

# need this so program can be monitored by monit
# make this a library function
def makePidFile(name):
    pid = os.getpid()
    
    pidFilename = "/var/run/rchpids/" + name + ".pid"
    fp=open(pidFilename,'w')
    print >> fp,pid
    fp.close()            
    #print "pid is " + `pid`
    return pid	# returns None if failed


def processLine(line,log):
    try:

        sensorId = "0080c7886b71"       # bug : MAC address of mars node : must be read from config
        
        line  = line.rstrip("\n")
        line2 = line.lower()
        
        print line
        
        # Do not scan Tweets for error messages
        if "SENDTWEET" in line :
            return None
  
        # Known issue in MaxMind library handling that is detracting from other problems
        if "error return without exception set" in line and " in geo_ip()" :
            return None
  
        # Ignore all non-error lines
        if "error" not in line2 and "reload" not in line2 and "shutdown" not in line2 and "exception" not in line2 and "failed" not in line2 and "failure" not in line2 and "died" not in line2  and "warning" not in line2 and "corrupt" not in line2 :
            return None
        else:
            print "Send honeypot platform error message to SplunkCloud\n=>" + line
        
        # Send to SplunkCloud 'Platform' Project (LaaS provider) 
        kojoney_loggly.sendToSplunkPlatform(sensorId,line,log)
                    
    except Exception,e:
        msg = "kojoney_splunk_platform.py : processLine() : " + e.__str__()
        print msg
        #syslog.syslog(msg)
    

# -------------------------------------------------------
        
# Start of code        
def main():
    try:        
        #print "Started"
        
        # Make pidfile so we can be monitored by monit        
        pid =  makePidFile("kojoney_splunk_platform")
            
        # Set the input filename to scan
        filename = '/var/log/messages'
        file = open(filename,'r')

        log = kojoney_splunk.StormLog(ACCESS_TOKEN, PROJECT_ID)
        
        # ------------
        # tail -f mode
        # ------------

        # Find the size of the file and move to the end
        st_results = os.stat(filename)
        st_size = st_results[6]
        file.seek(st_size)
        
        print "system     : Seek to end of /var/log/messages"
        
        while True:
            where = file.tell()
            line  = file.readline()
    
            if not line:		
                file.seek(where)
            else:			
                processLine(line,log)
    
            #print "sleeping..."
            # this can be a float for sub-second sleep    
            time.sleep(0.3)	# 10th of a second
    
    except Exception,e:
        msg = "kojoney_splunk_platform.py : exception : " + e.__str__()
        print msg
    
    
if __name__ == '__main__' :
    main()   
                                                                         