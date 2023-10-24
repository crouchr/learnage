#!/usr/bin/python

import time,sys,os , syslog , re 
import kojoney_hiddenip
#import kojoney_afterglow
import ipintellib

# Look for some obvious anomalies - i.e. services using non-standard ports
def isPadsAnomaly(ip,service,app,port):
    try:
        if service == "HTTP" and port != "80" and port != "8080" and port != "8081" :
            tweet = "PADS_ANOMALY,Non-standard port " + port + " used for " + service + " service on " + ip
            #print "isPadsAnomally() : " + tweet
            return tweet
            
        return None    
        
    except Exception,e:
        msg = "kojoney_pads_parse.py : isPadsAnomaly() : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return None
    
# input file
#asset,port,proto,service,application,time_first_discovered
#192.168.1.62,0,0,ARP,0:0C:29:A1:DD:89,1319179688
#192.168.1.64,0,0,ARP,0:0C:29:A1:DD:89,1319180259
#192.168.1.64,22,6,ssh,OpenSSH 5.1 (Protocol 2.0),1319180259
#192.168.1.63,0,0,ARP (Intel Corporation),0:04:23:3C:E3:F8,1319181827
#192.168.1.64,2222,6,ssh,OpenSSH 5.1p1 (Protocol 2.0),1319182621
#192.168.1.62,18080,6,www,Apache 2.2.6 (Unix),1319184113
#192.168.1.66,0,0,ARP,0:0C:29:A1:DD:89,1319193351
# return the Tweet or None

def processPads(line):
    
    try :
        #print "processPads() : line read is " + line

        # Ignore ARP logging
        if line.find("ARP") != -1 :
            return None

        # Ignore ICMP logging
        if line.find("ICMP") != -1 :
            return None
            
        # Ignore first line with column headings
        if line.find("asset,") != -1 :
            return None
            
        fields = line.split(",")
        ip = fields[0]
        #print "processPads() : ip=" + ip
        #print fields

        # make sure that the IP is not part of network services e.g. Twitter, Slackware etc.        
        #print "*** kojoney_pads_parse.py : calling hiddenIP() ***" 
        lanAllowed = False
        if kojoney_hiddenip.hiddenIP(ip,lanAllowed) == True :
            return None
                                             
        # Don't include our IP addresses since ANALYST will try to traceroute to it !
        if "192.168.1." in ip :
            perspective = "HONEYNET_SERVER"
            eventType   = "PADS_HONEYNET_SERVER"
            return None
        else: 
            perspective = "INET_SERVER"
            eventType   = "PADS_INET_SERVER"

        asInfo  = ipintellib.ip2asn(ip)
        dnsInfo = ipintellib.ip2name(ip)
        
        if "VODAFONE" in asInfo['registeredCode'].upper() or "VODANET" in asInfo['registeredCode'].upper():
            return None 
        
        # Port
        port = fields[1]
        
        # Service 
        service = fields[3].upper()
        if service == "WWW":
            service = "HTTP"
        
        appData     = fields[4]  
        if "(" in appData:
            app = appData.split('(')[0]
            app = app.rstrip(" ")
            appAddinfo = " " + appData.split('(')[1]
            appAddinfo = appAddinfo.lstrip(" ")
            appAddinfo = appAddinfo.rstrip(")")
        else:
            app = appData
            appAddinfo = ""
                 
        # Avoid a Tweet if nothing useful was learned
        if service == "UNKNOWN" and app.upper() == "UNKNOWN":
            return None


        # Ignore requests to send logs to Loggly - not sure what other services this will make invisible : bug
        if "TwistedWeb" in app :
            return None

        # Anything interesting in there ?
        anomalyTweet = isPadsAnomaly(ip,service,app,port)    
 
        #msg = perspective + "," + fields[0] + " : prot=" + fields[2] + " port=" + port + " svc=" + service + " app=" + app + " " + appAddinfo
        #msg = msg.rstrip(" ")
        #msg = eventType + "," + msg
        
        msg = fields[0] + " : prot=" + fields[2] + " port=" + port + " svc=" + service + " app=" + app + " " + appAddinfo
        msg = msg.rstrip(" ")
        msg = eventType + "," + msg
        
        msg = msg.replace("prot=1" ,"ICMP")
        msg = msg.replace("prot=6" ,"TCP")
        msg = msg.replace("prot=17","UDP")
        tweet = msg
 
        # Write to more useful log file
        logMsg = ip + "," + port + ',' + service + "," + app + "," + appAddinfo + "," + "AS" + asInfo['as'] + "," + asInfo['registeredCode'] + "," + dnsInfo['name'].rstrip('.') 
        fpOut = open('/home/var/log/pads-enhanced.log','a')
        print >> fpOut,time.ctime() + "," + logMsg
        print "processPads() : msg written to file : " + logMsg.__str__()
        fpOut.close()
     
        # Prepare list of Tweets       
        tweetList = []
        tweetList.append(tweet)
        if anomalyTweet != None :
            tweetList.append(anomalyTweet)
 
        return tweetList

    except Exception,e:
        msg = "kojoney_pads_parse.py : processPads() : " + `e` + " line=" + line
        print msg
        syslog.syslog(msg)
        return None
                               
# -------------------------------------------------------
        
# Start of code
# This is a test harness so comment/uncomment the relevent lines        
        
if __name__ == '__main__' :
       
# Set the input file to scan
    filename = '/home/var/log/pads-assets.csv'
    file = open(filename,'r')

    while True:
    
        # Tweets log file       
        # where = file.tell()
        line  = file.readline()
        line  = line.rstrip('\n')
        
        if not line:		# no data to process
            sys.exit()
        else :			# new data has been found
            tweetList = processPads(line)
            
        if tweetList != None:
            for tweet in tweetList:
                print "*** Tweet : " + tweet
                       
        #print "sleeping..."
        # this can be a float for sub-second sleep    
        time.sleep(0.1)		# 0.1 
                              
