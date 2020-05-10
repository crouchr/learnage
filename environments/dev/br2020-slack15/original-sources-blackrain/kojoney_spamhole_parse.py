#!/usr/bin/python

import time, os , syslog , re 
import ipintellib
import kojoney_spamholed_idmef

# Mar  8 06:06:14 mars spamhole[4445]: MAIL FROM: <k8fj899@kiss99.com>
# Mar  8 06:06:17 mars spamhole[4445]: Received: from ygx.34tja.org ([157.236.116.181]) by 81.149.188.217 with ESMTP id <302795-68827>; Thu, 08 Mar 2012 02:04:21 -0400

#Dec 23 07:37:50 mars spamhole[7213]: Checking host tracking file ipdb/1560389824...
#Dec 23 07:37:50 mars spamhole[7213]: Incoming connection received from 192.168.1.93
#Dec 23 07:37:50 mars spamhole[7213]: Spammer 192.168.1.93 has connected 1 times...
#Dec 23 07:37:50 mars spamhole[7213]: Incrementing connection counter...
#Dec 23 07:37:50 mars spamhole[7213]: Connection count 2 for 192.168.1.93 > MAX_CON 1 -> to the spamhole with ye !
#Dec 23 07:37:50 mars spamhole[7213]: Sending connection for 192.168.1.93 to SMTP relay...
#Dec 23 07:37:50 mars spamhole[7213]: Session transcript:
#Dec 23 07:37:50 mars spamhole[7213]: 220 mail.btconnect.com ESMTP
#Dec 23 07:38:06 mars spamhole[7213]: QUIT
#Dec 23 07:38:06 mars spamhole[7213]: 221 mail.btconnect.com Goodbye
#Dec 23 07:38:33 mars spamhole[7249]: Received connection
#Dec 23 07:38:33 mars spamhole[7249]: Checking host tracking file ipdb/1560389824...
#Dec 23 07:38:33 mars spamhole[7249]: Incoming connection received from 192.168.1.93
#Dec 23 07:38:33 mars spamhole[7249]: No previous connections from 192.168.1.93, initializing counter...
#Dec 23 07:38:33 mars spamhole[7249]: Connection count 1 for 192.168.1.93 <= MAX_CON 1 -> allowing e-mail passthrough
#Dec 23 07:38:33 mars spamhole[7249]: Sending connection for 192.168.1.93 to SMTP relay...
#Dec 23 07:38:33 mars spamhole[7249]: Session transcript:
#Dec 23 07:38:33 mars spamhole[7249]: 220 mail.btconnect.com ESMTP

# return the Tweet or None
def processSpamholed(line):
    
    try:
        line = line.rstrip('\n')

        #if "MAIL FROM:" not in line and "Receved: from " not in line :
        if "connection count " in line :  
            a = re.findall("(\d+\.\d+\.\d+\.\d+) hole=(\d+) connection count (\d+)",line)
            if len(a) > 0 :
                #print a.__str__()
                srcIP = a[0][0]
                hole  = a[0][1]
                count = a[0][2]
            else:
                srcIP = "0.0.0.0"        
                hole  = -1
                count = -1
            
            geoIP = ipintellib.geo_ip(srcIP)                                
            countryCode = geoIP['countryCode'].__str__()                     
            
            print "spammer IP               : " + srcIP
            print "spammer country code     : " + countryCode
            print "hole flag                : " + hole
            print "spammer connection count : " + count
                    
            if "allowing e-mail passthrough" in line :        
                passthrough = True
            else:
                passthrough = False   
        
            kojoney_spamholed_idmef.sendSpamholedIDMEF(srcIP,"192.168.1.61","10025","Spammer connected",count,passthrough,line)
        
        elif "HELO" in line.upper() or "EHLO" in line.upper() :
            a = re.findall("(\d+\.\d+\.\d+\.\d+) HOLETAG5:(.*)",line)
            if len(a) > 0 :
                #print a.__str__()
                srcIP   = a[0][0]
                ehloStr = a[0][1]
                
                geoIP   = ipintellib.geo_ip(srcIP)                                
                countryCode = geoIP['countryCode'].__str__()                     
                
                #print "********************"
                print "spammer IP               : " + srcIP
                print "spammer country code     : " + countryCode
                print "EHLO message             : " + ehloStr
                
                kojoney_spamholed_idmef.sendSpamholedEhloIDMEF(srcIP,"192.168.1.61","10025","Spammer said EHLO",ehloStr,line)
        
        elif "HOLETAG5:MAIL FROM:" in line.upper() :
            a = re.findall("(\d+\.\d+\.\d+\.\d+) holetag5:mail from:(.*)",line.lower())
            if len(a) > 0 :
                #print a.__str__()
                srcIP        = a[0][0]
                spammerEmail = a[0][1]
                
                geoIP   = ipintellib.geo_ip(srcIP)                                
                countryCode = geoIP['countryCode'].__str__()                     
                
                print "*****************************"
                print "spammer IP               : " + srcIP
                print "spammer country code     : " + countryCode
                print "spammer email            : " + spammerEmail
                
                kojoney_spamholed_idmef.sendSpamholedMailfromIDMEF(srcIP,"192.168.1.61","10025","Spammer said MAIL:FROM",spammerEmail,line)
                        
        return None

    except Exception,e:
        msg = "exception : " + e.__str__()
        print msg
        syslog.syslog("kojoney_spamhole_parse.py : processSpamholed() : " + `e` + " line=" + line)

        
# Start of code
# This is a test harness so comment/uncomment the relevent lines        
        
if __name__ == '__main__' :
       
# Set the input file to scan
    filename = '/home/var/log/spamhole.syslog'
    
    file = open(filename,'r')

    while True:
    
        # Tweets log file       
        # where = file.tell()
        line = file.readline()
        line = line.rstrip('\n')
        
        if not line:		# no data to process
            #print "No data"
            pass
        else :			# new data has been found
            #print "line before parsing = [" + line + "]"
            #msg = processAmunSubmit(line)
            print "----"
            msg = processSpamholed(line)
            #msg = processAmunDownload(line)
        
        if msg != None:
            print "line after parsing = [" + msg +"]"
                       
        #print "sleeping..."
        # this can be a float for sub-second sleep    
        time.sleep(0.01)		# 0.1 
                              
                 