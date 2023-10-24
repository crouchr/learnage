#!/usr/bin/python

# Tail the Suricata alert output log file and generate syslog events

import time, os , syslog , re , sys 
import kojoney_funcs

# only generate suricata NIDS events into syslog - only use syslog for non-IDS events during temporary debugging

# send a syslog from the main program
def doSyslog(msg):
    syslog.openlog("kojoney_suricata_syslog")		# Fake being the suricata IDS engine        
    syslog.syslog(msg)
    syslog.openlog("suricata")				# reset back to the fake program name


# Suricata IDS events
def processSur(line):
    try :
        line = line.rstrip("\n")
        print "line=" + line
                    
        # event is interesting so create syslog    
        fields = line.split(" ")
        print fields
        msg = ' '.join(fields[3:])
        msg = 'NIDS_SU,' + msg
        
        print "kojoney_suricata_syslog.py : processSur() : syslog to be generated : " + msg
        kojoney_funcs.appendGenericLogfile('/home/var/log/kojoney_surcata_syslog.debug','none',"syslog to be generated = " + msg)
        
        syslog.openlog("suricata")				# reset back to the fake program name
        syslog.syslog(msg)
        return
    
    except Exception,e:
        doSyslog("kojoney_suricata_syslog.py : processSur() : exception caught = " + `e` + " line=" + line)
                
# -------------        
# Start of code        
# -------------
syslog.openlog("suricata")		# Fake being the suricata IDS engine        
       
# Make pidfile so we can be monitored by monit        
pid =  kojoney_funcs.makePidFile("kojoney_suricata_syslog")
if pid == None:
    print "Failed to generate pidfile"
    sys.exit(0)
else:
    doSyslog("kojoney_suricata_syslog.py started with pid " + `pid`)
                
# Send an email to say kojoney_tail has started
now = time.time()
nowLocal = time.gmtime(now)
#makeMsg(0,"0","system,kojoney_viz started with pid=" + `pid` + " at localtime " + time.asctime(nowLocal))
a = "kojoney_suricata_syslog started with pid=" + `pid`

filenameSur          = '/home/var/log/suricata/suricata-fast.log'

# Stay in a loop until the file created by Suricata has been found
fileFound=False
while (fileFound == False):
    try:
        fileSur              = open(filenameSur,'r')
        print "fileSur = " + `fileSur`
        if fileSur != None:
            fileFound = True    
    except Exception,e:
        msg="kojoney_suricata_syslog.py : main() exception caught = " + `e`
        print msg
        doSyslog(msg)
        time.sleep(10)
        
# The file to be tailed has been found    
msg="kojoney_suricata_syslog.py : file " + filenameSur + " opened OK for first time"
print msg
doSyslog(msg)

# Wait for two minutes and then re-open the file   
msg="wait 120 seconds..."
print msg
doSyslog(msg)
time.sleep(120)		# 120
fileSur = open(filenameSur,'r')
msg = "kojoney_suricata_syslog.py : file " + filenameSur + " opened OK for second time"
print msg
doSyslog(msg)

msg="fileSur = " + `fileSur`
print msg
doSyslog(msg)

# Look for Suricata events
st_resultsSur = os.stat(filenameSur)
st_sizeSur    = st_resultsSur[6]
fileSur.seek(st_sizeSur)
print "system     : Seek to end of " + filenameSur

while True:

    try :    
        # Suricata - Snort engine replacement
        whereSur = fileSur.tell()
        lineSur  = fileSur.readline()
            
        if not lineSur:		# no data in feed
            #print "nothing in Suricata fast log file to process"
            fileSur.seek(whereSur)
        else :			# new data has been added to log file
            #print "*** NEW EVENT in Suricata IDS alert file to process !"
            processSur(lineSur)
                            
        #print "sleeping..."
        # this can be a float for sub-second sleep    
        time.sleep(0.5)			#  0.5 second
    
    except Exception,e:
        #syslog.syslog("kojoney_suricata_syslog.py : main() exception caught = " + `e`)
        sys.exit()
                                                            