#!/usr/bin/python

import time, os , syslog , re 
#import kojoney_amun_idmef
#import kojoney_idmef_common
#import ipintellib

# return the Tweet or None
def processConpot(line):
    
    try :
        #print "processAmunSubmit() : line read is " + line

        # Crude attempt to not Tweet error messages from the malware analysis sites
        #if line.find("problem") != -1 :		# Cwsandbox "Due to repeated hardware problems..."
        #    return None
        #if line.find("error") != -1 :		# not seen explicitly - just a guess
        #    return None
        
        #print "LINE=" + line
        
        #if line.find("New snmp session from") == -1 and line.find("request from ") == -1 :
        #    return None
        
        # If can't find 'session from' then ignore
        if line.find(" session from ") == -1 :
            return None
        
        # Extract attacker IP    
        pat = 'session from (\d+\.\d+\.\d+\.\d+)'
        
        ips = re.findall(pat,line)
        #print "srcIP = " + srcIP[0].__str__()  
        if len(ips) > 0 :
            #print ips
            srcIP   = ips[0]
            
            if 'modbus session' in line:
                sessionType = "ICS SCADA MODBUS connection from "
            elif 's7comm session' in line:
                sessionType = "ICS SCADA S7COMM connection from "
            elif 'snmp session' in line:
                sessionType = "SNMP request from "
            elif 'http session' in line:
                sessionType = "HTTP request from "
            else :
                sessionType = "Unknown connection from "                 
            
            msg = "CONPOT," + sessionType + srcIP 
            #print msg
            return msg
        else :
            return None

    except Exception,e:
        syslog.syslog("kojoney_conpot_parse.py : processConpot() : " + `e` + " line=" + line)

                                               
# -------------------------------------------------------
        
# Start of code
# This is a test harness so comment/uncomment the relevent lines        
        
if __name__ == '__main__' :
       
# Set the input file to scan
    #filename = '/usr/local/src/amun/logs/testcases/submissions.log'
    #filename = '/usr/local/src/amun/logs/testcases/exploits.log'
    filename = '/home/var/log/conpot.syslog'
    file = open(filename,'r')

    while True:
    
        # Tweets log file       
        # where = file.tell()
        line  = file.readline()
        line=line.rstrip('\n')
        
        if not line:		# no data to process
            pass
        else :			# new data has been found
            msg = processConpot(line)
        
        if msg != None:
            print "line before parsing = {" + line + "}"
            print "line after parsing  = [" + msg  + "]"
            print " "
                       
        #print "sleeping..."
        # this can be a float for sub-second sleep    
        time.sleep(0.02)		# 0.1 
                              
                 