#!/usr/bin/python

import time, os , syslog , re , sys
import mailalert
import kojoney_idmef_common
import kojoney_clamd_idmef
import kojoney_attacker_event

# Jan 11 05:59:06 mars clamd[3812]: /tmp/212.205.117.15:80-192.168.1.67:46273: Trojan.Perl.Shellbot FOUND
# return the Tweet or None

def processClamd(line,sensorId,txnId):
    
    try :
        
        # Other messages are logged to the file
        if " FOUND" not in line:
            return None
            
        if "Heuristics.Structured" in line:	# credit card numbers , SSN - false positives probably
            return None
        
        ips = re.findall("(\d+\.\d+\.\d+\.\d+):(\d+)\-(\d+\.\d+\.\d+\.\d+):(\d+)",line)
        if len(ips) > 0 :
            #print ips
            srcIP   = ips[0][0]
            srcPort = ips[0][1]
            dstIP   = ips[0][2]
            dstPort = ips[0][3]
            
            #print srcIP
            #print srcPort
            #print dstIP   
            #print dstPort 
            
            fields = line.split(" ")
            #print fields
            malware = fields[6]
            #print malware              
            
            tweet = "CLAMD," + "Malware " + malware + " in flow from " + srcIP + " ports={s=" + srcPort + " d=" + dstPort + "}"
            
            # Send email since this is a very interesting event
            if sensorId != "TEST":
                destination = ['majoralert999@gmail.com','richard_crouch@btconnect.com']
                mailalert.mailalert("richard_crouch@btconnect.com",destination,'smtp.btconnect.com',"BlackRain : Malware captured",tweet,False)
                #kojoney_alert_client
            
                # Update SIEM
                kojoney_clamd_idmef.sendFlowClamdIDMEF(sensorId,srcIP,srcPort,dstIP,dstPort,malware,line,tweet)    

            # Update attacker database
            kojoney_attacker_event.generateAttackerEvent(txnId,srcIP,None,sensorId,"MWARE","CLAMD",None,"Malware found in network flow",None,None,malware,None,None)
            return tweet
                     
        return None

    except Exception,e:
        msg = "kojoney_clamd_parse.py : processClamd() : " + e.__str_() + " line=" + line
        print msg
        syslog.syslog(msg)


                               
# -------------------------------------------------------
        
# Start of code
# This is a test harness so comment/uncomment the relevent lines        
        
if __name__ == '__main__' :
       
# Set the input file to scan
    filename = '/home/var/log/clamd.syslog'
    file = open(filename,'r')

    while True:
    
        # Tweets log file       
        # where = file.tell()
        line  = file.readline()
        line  = line.rstrip('\n')
        #print "line is : " + line
        
        if not line :		# no data to process
            sys.exit("No more data to parse")
        else :			# new data has been found
            #if "GET"  in line.upper():
            #if "POST" in line.upper():
            #if "MAIL" in line.upper():
            #if "successfully opened" in line:
            #if "o attack found" in line:
            if " FOUND" in line :
                msg = processClamd(line,"TEST",123)
                if msg != None:
                    print "*** Tweet : " + msg
                       
        #print "sleeping..."
        # this can be a float for sub-second sleep    
        time.sleep(0.2)		# 0.2 
                              
    