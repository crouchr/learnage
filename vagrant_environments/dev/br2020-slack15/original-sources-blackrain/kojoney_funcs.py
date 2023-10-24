#!/usr/bin/python
import time
import os
import re

def makePidFile(name):
    pid = os.getpid() 
        
    pidFilename = "/var/run/rchpids/" + name + ".pid"
    fp=open(pidFilename,'w')
    print >> fp,pid
    fp.close()     
    #print "pid is " + `pid`
    return pid  # returns None if failed

# Find first IP address in line
def findFirstIP(line):
    ip=None
    pat = r'\d+\.\d+\.\d+\.\d+'             # locate a number of IP addresses
    ips = re.findall(pat,line)
    if len(ips) != 0 :
        ip = ips[0]
    #print "kojoney_funcs.py findFirstIP(): first IP address found = " + ip
    return ip                                            

# Write netflow payload to a file to search
# this now obsoleted by writeDefConEvent() function below
# DO NOT USE
def logDefconEvent(msg):
    now = time.time()
    #nowLocal = time.gmtime(now)  
    nowLocal = time.localtime(now)
    msg = time.asctime(nowLocal) + " " + msg
    
    fp = open(r'/home/var/log/defconf_events.log',"a")
    print >> fp,msg
    fp.close()
    print "**** Logged defcon event to file : " + msg


# This file used to only be netflow events  but now it is all defcon related events
# e.g. src=botwall
# This file is parsed by regexp in sec.pl so add the timestamp to the end where it is not used...
def writeDefconEvent(src,line):
    now = time.time()  
    nowLocal = time.localtime(now)

    # file needs to be touched - is this the daily file ?
    msg = src + ":" + line + " at " + time.asctime(nowLocal)
    print "kojoney_funcs.py : writeDefconEvent() : msg =" + msg
    
    fpOut = open(r'/home/var/log/netflow_events.log','a')
    print >> fpOut,msg
    fpOut.close()

# Make he other functions in this file use this function
def appendGenericLogfile(filename,src,line):
    now = time.time()  
    nowLocal = time.localtime(now)

    # file needs to be touched - is this the daily file ?
    msg = src + ":" + line + " at " + time.asctime(nowLocal)
    print "kojoney_funcs.py : appendGenericLogfile() : msg =" + msg
    
    fpOut = open(filename,'a')
    print >> fpOut,msg
    fpOut.close()


def calcLocalTime(longitude):
    if int(longitude) > 360 :   # GeoIP returns 999.0 if failed
        offsetSecs = 0;
    else:    
        offsetSecs = 3600 * int(longitude / 15)
                            
    now = time.time()
    localTime = now + int(offsetSecs)
                                        
    print "offsetSecs        : " + `offsetSecs`
    print "localTime (epoch) : " + `localTime` 
    timeTuple = time.localtime(localTime)
    print "localTime         : " + time.asctime(timeTuple)
                                                            
    return time.asctime(timeTuple)
                                                                
                                                                

    
if __name__ == "__main__":
    logDefconEvent("This is a test event - ignore it")
    writeDefconEvent("test","This is a test event - ignore it")
    
    