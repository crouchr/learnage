#!/usr/bin/python

import time, sys, os , syslog , re 
import kojoney_p0f_lib
import kojoney_snort_funcs
import kojoney_hiddenip
import kojoney_honeytrap_idmef
import kojoney_attacker_event
import ipintellib
        
# input file

#honeytrap v1.0.0 Copyright (C) 2005-2007 Tillmann Werner <tillmann.werner@gmx.de>
#[2011-11-01 23:54:12] ---- Trapping attacks via NFQ. ----
#[2011-11-02 00:18:03]    1433/tcp         Connection from 222.189.239.245:5508 accepted.
#[2011-11-02 00:18:05]  * 1433/tcp         160 bytes attack string from 222.189.239.245:5508.
#[2011-11-02 04:42:04]    1433/tcp         Connection from 222.189.239.245:5410 accepted.
#[2011-11-02 04:42:06]  * 1433/tcp         160 bytes attack string from 222.189.239.245:5410.
#[2011-11-02 05:19:17] ---- honeytrap stopped ----
# return the Tweet or None

def processHoneytrap(txnId,sensorId,line):
    
    try :
        line = line.rstrip("\n")
        print "processHoneytrap() : line read is " + line

        # Only interested in certain events
        #if line.find("Connection from ") == -1 and line.find(" attack string from ") == -1 :
        if line.find(" attack string from ") == -1 :	# only interested if attacker sends data
            return None
        
        # Where is the attack coming from ?
        fields = re.findall("(\d+\.\d+\.\d+\.\d+)\:(\d+)",line)
        if len(fields) > 0 :
            srcip   = fields[0][0]
            srcPort = fields[0][1]
        else:
            srcip   = "None"
            srcPort = "None"    
        
        #print "srcIP   = " + srcip
        #print "srcPort = " + srcPort

        fields = re.findall("(\d+) bytes attack string from",line)
        if len(fields) > 0 :
            bytes = fields[0]
        else:
            bytes = "0"
        #print "bytes = " + bytes

        fields = re.findall("(\d+)\/tcp",line)
        if len(fields) > 0 :
            dport = fields[0]
        else:
            dport = "None"
        #print "dport = " + dport

        dstip = "192.168.1.60"	# bug -> hard-coded dst IP
        
        # Not interested in events originating from LAN 
        print "*** kojoney_honeytrap_parse.py : calling hiddenIP() ***" 
        if kojoney_hiddenip.hiddenIP(srcip) == True :
            return None
        
        p0fDict = kojoney_p0f_lib.getp0f(srcip,dstip,dport)
        if p0fDict != None:
            p0f = " p0f=" + p0fDict['genre_short'] + " hops=" + p0fDict['hops'] + " up=" + p0fDict['uptime']
        else:
            p0f = ""

        tweet = "HTRAP," + srcip + ":" + srcPort + " -> " + dstip + ":" + dport + " [bytes=" + bytes + p0f + "]"	# bug -> hard-coded dest IP !!!
        print tweet
        
        geoIP = ipintellib.geo_ip(srcip)                                
        countryCode = geoIP['countryCode'].__str__()    
        kojoney_honeytrap_idmef.sendHoneytrapIDMEF(srcip,dstip,dport,p0f,line)
        
        # Update Attacker Database
        addInfo1   = "proto=TCP:dPort=" + dport.__str__() + ":" + "bytes=" + bytes.__str__()
        addInfo2   = None
        attackerIP = srcip
        kojoney_attacker_event.generateAttackerEvent(txnId,attackerIP,p0fDict,sensorId,"SCANNING","HONEYTRAP",None,"Established incoming connection",None,None,None,addInfo1,addInfo2)
                                
        
        # Replace destination IP with text
        tweet = kojoney_snort_funcs.snortTwittifyLite(tweet)
        
        return None	# no need to Tweet now we have SIEM
        #return tweet

    except Exception,e:
        msg = "kojoney_honeytrap_parse.py : processHoneytrap() : " + `e` + " line=" + line
        print msg
        syslog.syslog(msg)
        return None
                               
# -------------------------------------------------------
        
# Start of code
# This is a test harness so comment/uncomment the relevent lines        
        
if __name__ == '__main__' :
       
    print "Started"
    
# Set the input file to scan
    filename = '/home/var/log/honeytrap.log'
    file = open(filename,'r')
    print filename
    
    while True:
    
        line  = file.readline()
           
        if not line:		# no data to process
            print "No more data to process, so exit."
            sys.exit()
        else :
            line = line.rstrip('\n')			# new data has been found
            msg = processHoneytrap(124,"TEST",line)
            
        if msg != None:
            print "   Tweet : " + msg
                       
        #print "sleeping..."
        # this can be a float for sub-second sleep    
        time.sleep(0.1)		# 0.1 
                              
