#!/usr/bin/python

import time, os , syslog , re 
#import kojoney_amun_idmef
#import kojoney_idmef_common
import ipintellib

import kojoney_tsom


# tstamp=Sat May 18 10:32:24 2013, ip=202.91.239.212, cc=CN, flags="PR SC", P1CTLpeak=3.0, city="None", rdns=NoDNS, net=AS4837, isp="CHINA169-BACKBONE", os=WIN, createEpoch=Sat May 18 10:27:13 2013, pruneEp
#och=Sat May 18 10:32:24 2013, lifetimeSecs=311.3
#tstamp=Sat May 18 10:33:05 2013, ip=199.59.149.230, cc=US, flags="PR", P1CTLpeak=1.0, city="San Francisco", rdns=www4.twitter.com, net=AS13414, isp="TWITTER-NETWORK", os=none, createEpoch=Sat May 18 10:27
#:57 2013, pruneEpoch=Sat May 18 10:33:05 2013, lifetimeSecs=307.5
#tstamp=Sat May 18 10:33:45 2013, ip=119.93.21.166, cc=PH, flags="SC", P1CTLpeak=3.0, city="Philippine", rdns=119.93.21.166.static.pldt.net, net=AS9299, isp="IPG-AS-AP", os=none, createEpoch=Sat May 18 10:
#28:39 2013, pruneEpoch=Sat May 18 10:33:45 2013, lifetimeSecs=306.4
#tstamp=Sat May 18 10:39:34 2013, ip=60.195.250.56, cc=CN, flags="SC", P1CTLpeak=3.0, city="Beijing", rdns=NoDNS, net=AS4847, isp="CNIX-AP", os=LNX, createEpoch=Sat May 18 10:34:29 2013, pruneEpoch=Sat May
# 18 10:39:34 2013, lifetimeSecs=304.8
# tstamp=Sat May 18 10:41:57 2013, ip=202.91.239.212, cc=CN, flags="PR SC", P1CTLpeak=3.0, city="None", rdns=NoDNS, net=AS4837, isp="CHINA169-BACKBONE", os=WIN, createEpoch=Sat May 18 10:36:43 2013, pruneEp
# och=Sat May 18 10:41:57 2013, lifetimeSecs=314.0
 

# return the Tweet or None
def processTSOM(txnId,sensorId,line):
    
    try :
        
        # Disable Tweets - code works but just no good in Tweets
        #return None
            
        #print "processTsom() : line read is " + line
        fields = line.split(",")
        #print fields
        
        srcIP = fields[1]
        srcIP = srcIP.split("=")[1]
        
        ctl = fields[4]
        if "P1" in ctl:
            lifetimeID = "Short-term"
        else:
            lifetimeID = "Long-term"    
        ctl = ctl.split("=")[1]

        # Short-term is not interesting to Tweet until I have debugged it
        if lifetimeID == "Short-term":
            return None
            
        # flags
        flags = fields[3].split("=")[1]
        flags = flags.lstrip('"')
        flags = flags.rstrip('"')
        #print flags        
      
        # Ignore if prelude or prelude SIEM
        if "192.168.1.73" in srcIP or "192.168.1.74" in srcIP :
            return None
        
        # Only tweet if something interesting happened
        interesting = False
        for phase in ['AT','GA','MA','MW','CT','HU']:
            if phase in flags :
                interesting = True 
        
        if interesting == False:
            return None
 
        if "lifetimeSecs" in line:
            lifetimeSecs = line.split("lifetimeSecs=")[1] 
        else:
            lifetimeSecs = 0.0
                     
        if float(ctl) > 0.0 :	# 1.0 = PRODUCTION , 0.0 = TEST : Must exceed min threshold
            #msg = "REPORT," + lifetimeID + " Threat Level for " + srcIP + " is " + "%.1f" % float(ctl) + ", flags={" + kojoney_tsom.orderFlags(flags).rstrip(" ") + "}" 
            msg = "REPORT,Threat Level for " + srcIP + " is " + "%.1f" % float(ctl) + ", flags={" + kojoney_tsom.orderFlags(flags).rstrip(" ") + "}" 
            return msg
        else:
            return None
            
    except Exception,e:
        msg = "kojoney_tsom_parse.py : processTsom() : " + e.__str__() + " line=" + line
        print msg
        syslog.syslog(msg)
        
                               
# -------------------------------------------------------
        
# Start of code
# This is a test harness so comment/uncomment the relevent lines        
        
if __name__ == '__main__' :
       
    # Set the input file to scan
    #filename = '/home/var/log/tsom_dump_test.csv'
    filename = '/home/var/log/tsom_dump.csv'
    file = open(filename,'r')

    while True:
    
        # Tweets log file       
        # where = file.tell()
        line = file.readline()
        line = line.rstrip('\n')
        
        if not line:		# no data to process
            pass
        else :			# new data has been found
            #print "line before parsing = [" + line + "]"
            #msg = processAmunSubmit(line)
            #msg = processAmunExploit(line)
            msg = processTSOM(123,"TEST",line)
        
        if msg != None:
            print "*** Tweet : [" + msg +"]"
                       
        #print "sleeping..."
        # this can be a float for sub-second sleep    
        time.sleep(0.02)		# 0.1 
                              
                 