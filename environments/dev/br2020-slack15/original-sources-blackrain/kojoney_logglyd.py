#!/usr/bin/python

# Tail the Tweet Queue and send data to SplunkCloud LaaS and to MongoDB

import sys, time, os , syslog , urlparse , re 
import kojoney_loggly
import kojoney_splunk
from pymongo import MongoClient
from pprint import pprint

# SplunkCloud credentials 
ACCESS_TOKEN = 'bhCSxrbWx9tRwoycO-Jf1Dh-KDBUQ01c_BbrTsPfaJVtRzvPdOT8JgKcKnuEjQYZLt5MZs1YKxM='
PROJECT_ID   = '45f7b0f416a311e483a622000a9e07fe'

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

def map2cif(sdata):
    '''
    Map MongoDB data to CIF format
    '''
    try :
        cifdata = {}
        if 'ip' not in sdata : # must have an IP for CIF data 
            return None 
            
        if sdata['eventType'] not in ['WEB_SCN','KIPPO','IPLOG','SNORT_NIDS','TELNETD','SMTPD'] :
            return None
            
        cifdata['otype'] = "ipv4"
        cifdata['observable'] = sdata['ip']
        
        cifdata['confidence'] = "20"
        cifdata['group'] = "everyone"
        cifdata['tlp'] = "green"
        cifdata['provider'] = "BlackRain Honeypot @honeytweeter"
        cifdata['description'] = "BlackRain honeypot : " + sdata['eventType']    
        cifdata['tags'] = ['honeypot','blackrain']
            
        print "CIF data : " + cifdata.__str__()
        return cifdata    
            
    except Exception,e:
        msg = "kojoney_logglyd.py : map2cif : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return None

# Wrapper function to send the Tweet to various external databases
# Return None if no need to process the data
def processTweet(line) :
    try:

        sensorId = "0080c7886b71"       # bug : MAC address of mars node : must be read from config
        
        line = line.rstrip("\n")
        #print line
        line = line.split("tweet=")[1]
        rawLine = line
        
        # Do not process GURU Tweets - no point - all this meta data can be derived from the IP
        if "GURU," in line:
            return None
        
        # fixme : These messages need to be picked up earlier but drop them for now
        if ("in geo_ip)") in line:
            return None
        
        # Send to SplunkCloud LaaS provider and return the JSON record in sdata for use by other destinations  
        # return None is also an option
        sdata = kojoney_loggly.sendToLoggly(sensorId,line)
        
        #cifdata = map2cif(sdata)
        #print  "cifdata = " + cifdata.__str__()
        
        # got to here -> send cifdata to CIF server...
        
        # Store JSON document in MongoDB database
        #mongoResult = attacks.insert(sdata)
        
        #if mongoResult == None :
        #    print "kojoney_logglyd.py : Error inserting attack into MongoDB : sdata = " + sdata.__str__()
        #    return False
        #else:
        #    print "kojoney_logglyd.py : Successfully inserted attack into MongoDB : sdata = " + sdata.__str__()
        #    return True
        
        return sdata
                        
    except Exception,e:
        msg = "kojoney_logglyd.py : processTweet : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return None

# -------------------------------------------------------
        
# Start of code        
def main():
    try:        
        print "Started"
        
        # Make pidfile so we can be monitored by monit        
        pid =  makePidFile("kojoney_logglyd")
            
        #syslog.openlog(logoption=syslog.LOG_PID,"kojoney_logglyd")
        syslog.openlog("kojoney_logglyd")
            
        # Set the Kojoney Tweet Queue input filename to scan
        filename = '/home/var/log/tweet_queue.log'
        #filename = '/home/var/log/test_tweet_queue.log'
        file = open(filename,'r')
        
        # Create connection to Splunk
        #print "Connecting to SplunkStorm..."
        #splunk = kojoney_splunk.StormLog(ACCESS_TOKEN, PROJECT_ID)
        #print "SplunkStorm = " + splunk.__str__()
        splunk = None
        
        # Create connection to MongoDB on Mail (or Shuttle PC)
        #print "Connecting to Mongodb..."
        #client = MongoClient('mongodb://mail:27017')
        #print "Mongodb client = " + client.__str__()
        
        #db = client.blackrain
        #collection = db.blackrain_collection
        #attacks = db.attacks
        attacks = None
        
        # ------------
        # tail -f mode
        # ------------

        # Find the size of the Tweet file and move to the end
        st_results = os.stat(filename)
        st_size = st_results[6]
        file.seek(st_size)
        
        # Find the size of the Kippo commands file and move to the end
        kippo_file = open("/home/var/log/kippo-all-cmds.csv",'r')
        kippo_results = os.stat("/home/var/log/kippo-all-cmds.csv")
        kippo_size = kippo_results[6]
        kippo_file.seek(kippo_size)
      
        print "kojoney_logglyd     : Seek to end of monitored files..."
        
        while True:
                   
            where = file.tell()
            line  = file.readline()

            # fixme : does this work ?
            #kippo_where = kippo_file.tell()
            #kippo_line  = kippo_file.readline()

            if not line:		
                #print time.ctime() + " : Nothing in Kojoney Tweet Queue (" + filename + ") to process..."
                file.seek(where)
            else:			
                print "kojoney_logglyd.py : *** NEW EVENT in Kojoney Tweet Queue to process !"
                sdata = processTweet(line)
                if sdata != None :
                    print "=================================="
                    print time.ctime()
                    print "Send JSON event to local syslog-ng"
                    print "=================================="
                    pprint(sdata)
                    syslog.syslog(sdata.__str__())
                        
            #if not kippo_line :
            #    print time.ctime() + " : Nothing in Kojoney Kippo Commands Log to process..."
            #    kippo_file.seek(kippo_where)
            #else:			
            #    print "kojoney_logglyd.py : *** NEW EVENT in Kojoney Kippo Commands Log to process !"
            #    print line
                #sdata = processKippoCmd(line)
                #if sdata != None :
                #    syslog.syslog(sdata.__str__())
             
            #print "sleeping..."
            # this can be a float for sub-second sleep    
            time.sleep(1)	# 10th of a second
    
    except Exception,e:
        msg = "kojoney_logglyd.py : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
    
    
if __name__ == '__main__' :
    main()   
                                                                         