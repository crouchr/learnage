#!/usr/bin/python

import time, sys, os , syslog , re 
import kojoney_defend
import kojoney_iplog_idmef
import kojoney_attacker_event
import syslog

# input file
#Oct 23 17:32:40 TCP: SYN scan detected [port 80] from 192.168.1.92 [ports 1846,1847,1848,1849,1850,...]
#Oct 23 17:33:32 TCP: SYN scan mode expired for 192.168.1.92 - received a total of 35 packets (700 bytes).
#Feb 14 07:50:43 UDP: scan/flood detected [port 161] from 192.168.1.247 [ports 54535,54849,54370,41945,34939,...]
#Feb 14 07:50:10 TCP: TCP port scan detected [port 2222] from 193.106.172.96 [ports 33631,33998,34363,34701,35034,...]
#Feb 14 07:50:11 TCP: TCP SYN scan detected [ports 25,143,1025,110,587,139,445,554,3372] from 95.22.12.194 [port 36703]

# return the Tweet or None

def processIplog(txnId,sensorId,line):
    
    try :
        #print "processIplog() : line read is " + line

        # Only interested in scan and flood (start and end) events
        if line.find(" expired for ") == -1 and line.find(" scan detected ") == -1 and line.find(" scan/flood detected ") == -1 :
            return None
        
        # Where is the scan coming from ?
        srcip = re.findall("\d+\.\d+\.\d+\.\d+",line)
        if len(srcip) > 0 :
            srcip = srcip[0]
        else:
            srcip = "None"    
        #print srcip
        
        # Not interested in scan from LAN - includes syslog bursts from ADSL router etc false positives
        if srcip.find("192.168.1.") != -1 :
            return None

        # Not interested in false alerts from Google DNS
        if srcip.find("8.8.8.8") != -1 :
            return None
        
        if  "SYN scan detected" in line :
            scanType = "SYN scan"
        elif "TCP port scan detected" in line :
            scanType = "TCP scan"
        elif "UDP: scan/flood detected" in line :
            scanType = "UDP scan"
        else:
            scanType = "Port scan"	# generic - this value should never be used    
        
        # bug - single port was targetted               
        ports = re.findall("\[port (\d+)\]",line)
        if len(ports) > 0:
            port = ports[0]
        else :
            port = "-1"
        
        msg = line[16:] 	   			# skip timestamp
        msg = msg.replace(":","")
        msg = msg.replace("mode ","")
        msg = msg.replace("port scan", "portscan")	# less ambigious when grepping for
        tweet = "IPLOG," + msg	
        
        # Update Prelude SIEM
        kojoney_iplog_idmef.portScanIDMEF(srcip,scanType,port,line)
        
        # Update Attacker Database
        addInfo1 = None
        addInfo2 = None
        kojoney_attacker_event.generateAttackerEvent(txnId,srcip,None,sensorId,"PSCAN","IPLOG",None,scanType,None,None,None,addInfo1,addInfo2)
                
        # active response against certain ports - but not Microsoft ones
        ACTIVEPORTLIST = ['22','23','25'] # list of ports to add blackholes for 
        if line.find(" scan detected ") == -1 and line.find(" scan/flood detected ") == -1 :
            return None
        else :
            if port in ACTIVEPORTLIST:
                bh_tweet = kojoney_defend.blackhole(txnId,sensorId,srcip)       
                #if bh_tweet == None:
                #    return None
            else:
                bh_tweet = None
                            
        # construct return list of tweets
        tweets = []
        tweets.append(tweet)
        if bh_tweet != None:
            tweets.append(bh_tweet)
        
        return tweets

    except Exception,e:
        msg = "kojoney_iplog_parse.py : processIplog() : " + `e` + " line=" + line
        print msg
        syslog.syslog(msg)
        return None

                               
# -------------------------------------------------------
        
# Start of code
# This is a test harness so comment/uncomment the relevent lines        
        
if __name__ == '__main__' :
       
# Set the input file to scan
    #filename = '/home/var/log/iplog.log'
    filename = '/home/crouchr/iplog-test.log'
    file = open(filename,'r')

    while True:
    
        # Tweets log file       
        # where = file.tell()
        line  = file.readline()
        line  = line.rstrip('\n')
        
        if not line:		# no data to process
            sys.exit()
        else :			# new data has been found
            print line
            tweets = processIplog(123,"TEST",line)
            
        if tweets != None and len(tweets) != 0 :
            for tweet in tweets :
                print "*** Tweet : " + tweet
                       
        #print "sleeping..."
        # this can be a float for sub-second sleep    
        time.sleep(0.1)		# 0.1 
                              