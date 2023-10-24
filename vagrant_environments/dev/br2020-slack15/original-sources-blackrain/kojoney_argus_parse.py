#!/usr/bin/python

import time, sys, os , syslog , re 
import kojoney_p0f_lib
import kojoney_snort_funcs
import kojoney_argus_idmef
import kojoney_hiddenip
import kojoney_attacker_event

# input file
# StartTime      Flgs  Proto            SrcAddr  Sport   Dir            DstAddr  Dport  TotPkts   TotBytes State 
# 06:51:43.714981  e s         tcp     187.45.224.142.1460      ->       192.168.1.66.139           2        124     s
# 06:51:52.623489  e s         tcp     187.45.224.142.1460      ->       192.168.1.66.139           1         62     s
# 06:52:04.832184  e s         tcp     187.45.224.142.3132      ->       192.168.1.66.139           2        124     s
# 06:52:13.872700  e s         tcp     187.45.224.142.3132      ->       192.168.1.66.139           1         62     s
# 06:52:53.170939  e s         tcp     187.45.224.142.3699      ->       192.168.1.66.139           2        124     s
# 06:53:02.799488  e s         tcp     187.45.224.142.3699      ->       192.168.1.66.139           1         62     s
# 06:53:29.337000  e s         tcp     187.45.224.142.4396      ->       192.168.1.66.139           2        124     s
# 06:53:38.417517  e s         tcp     187.45.224.142.4396      ->       192.168.1.66.139           1         62     s
# 06:53:50.230191  e s         tcp     187.45.224.142.2244      ->       192.168.1.66.139           2        124     s
# 06:53:59.542721  e s         tcp     187.45.224.142.2244      ->       192.168.1.66.139           1         62     s
# 06:54:33.208640  e s         tcp     187.45.224.142.1970      ->       192.168.1.66.139           2        124     s
# 06:54:42.037143  e          icmp       4.79.142.206.0x0008   <->       192.168.1.66.0x0000        2        102   ECO
# 06:54:42.077145  e           tcp       4.79.142.206.63060     ->       192.168.1.62.18080         5        296   sSR

# 07:58:57.461331  e s         tcp     187.45.224.142.2678      ->       192.168.1.66.139           1         62     s
# 07:59:09.986045  e s         tcp     187.45.224.142.1917      ->       192.168.1.66.139           2        124     s
# 07:59:18.930555  e s         tcp     187.45.224.142.1917      ->       192.168.1.66.139           1         62     s
# 07:59:43.103932  e i         tcp     200.107.121.33.55165     ->       192.168.1.60.3389         13        795   sSE
# 07:59:48.496240  e           tcp     200.107.121.33.55165     ->       192.168.1.60.3389         10        575   sSE
# 07:59:53.652534  e           tcp     200.107.121.33.55165     ->       192.168.1.60.3389          4        229 sSEfF

# return the Tweet or None

def processArgus(txnId,sensorId,line):
    
    try :
        addInfo1 = None
        addInfo2 = None
        
        line = line.rstrip("\n")
        print "processArgus() : line read is " + line
        
        # Ignore file headers
        if line.find("StartTime") != -1 :
            return None

        protocols = re.findall("icmp|tcp|udp",line)
        if len(protocols) > 0 :
            protocol = protocols[0].upper()
        else:
            protocol = "OTHER"    
        #print "protocol = " + protocol

        fields = line.split()
        #print fields
        state = fields[-1]
        
        if state == "s" and protocol == "TCP" :		# SYN scanning
            return None
   
        if state == "sS" and protocol == "TCP" :	# SYN scanning - honeypot has responded with SYN/ACK
            return None

        if state == "sSR" and protocol == "TCP" :	# SYN scanning - honeypot has responded with SYN/ACK and then session is RESET
            return None
   
        bytes = fields[-2]
        pkts  = fields[-3]
        dir   = fields[-5]
        
        if int(bytes) >= 1024 or int(pkts) >= 32 :
            size = "Long "
        else :
            size = ""    
                
        #print "state = " + state
                
        # Where is the scan coming from ?
        ips = re.findall("(\d+\.\d+\.\d+\.\d+)\.(\d+)",line)
        if len(ips) > 0 :
            #print ips
            srcip = ips[0][0]
            sport = ips[0][1]
            dstip = ips[1][0]
            dport = ips[1][1]
        else:
            #print "Can't locate all fields for a flow, so return"
            return None
              
        #print srcip + " -> " + dstip
        
        # Not interested in scan from LAN - includes syslog bursts from ADSL router etc false positives
        #if srcip.find("192.168.1.") != -1 :
        #    return None
        print "*** kojoney_argus_parse.py : calling hiddenIP() ***"         
        if kojoney_hiddenip.hiddenIP(srcip) == True :
            return None
                    
        # Not interested in false alerts from Google DNS
        #if srcip.find("8.8.8.8") != -1 :
        #    return None

        #msg = line[16:] 	   	# skip timestamp
        #msg = msg.replace(":","")
        #msg = msg.replace("mode ","")
        #msg = msg.replace("port scan", "portscan")	# less ambigious when grepping for

        p0fDict = kojoney_p0f_lib.getp0f(srcip,dstip,dport)
        
        # How to solve this more pythonically ???
        #print p0fDict.__str__()
        if p0fDict.__str__() != "None":
            #p0f = " p0f=" + p0fDict['genre_short'] + " hops=" + p0fDict['hops'] + " link=" + p0fDict['link'] + " up=" + p0fDict['uptime']
            p0f = " p0f=" + p0fDict['genre_short'] + " hops=" + p0fDict['hops'] + " up=" + p0fDict['uptime']
            p0fOS = p0fDict['genre_short']
            p0fHops = p0fDict['hops']
        else:
            p0f = ""            
            p0fOS   = "Unknown"
            p0fHops = "Unknown"

        if "192.168.1." in srcip and "192.168.1." in dstip :
            FLOW_TYPE = "AFLOW"
        elif dir == "->" and srcip.find("192.168.1.") >= 0 :	# bug : make this a generic function
            FLOW_TYPE = "AFLOW_OUT"
        elif dir == "->" and srcip.find("192.168.1.") < 0 :
            FLOW_TYPE = "AFLOW_IN"
        else:
            FLOW_TYPE = "AFLOW"        
        print "FLOW_TYPE : " + FLOW_TYPE
            
        msg = srcip + ":" + sport + " " + dir + " " + dstip + ":" + dport + " state=" + state + " pkts=" + pkts + " bytes=" + bytes + p0f
        tweet = FLOW_TYPE + "," + msg	
        
        # Replace destination IP with text
        tweet = kojoney_snort_funcs.snortTwittifyLite(tweet)
        
        # construct return list of tweets
        tweets = []
        tweets.append(tweet)
        
        # Send event to Prelude
        kojoney_argus_idmef.sendArgusIDMEF(srcip,dstip,dport,protocol,dir,state,pkts,bytes,p0fOS,p0fHops,FLOW_TYPE)
 
        # Update Attacker Database        
        attackerIP  = srcip
        phase       = "SCANNING"
        eventSource = "ARGUS"
        eventId     = None
        eventDesc   = FLOW_TYPE
        MD5         = None
        virusVendor = None
        virusName   = None
        addInfo1    = "state=" + state + ":" + "proto=" + protocol + ":" + "dPort=" + dport.__str__() + ":" + "bytes=" + bytes.__str__() + ":" + "pkts=" + pkts.__str__()
        
        # Treat outbound flows as accessing malware download site etc : TCP for HTTP/SSH and UDP for TFTP
        if (protocol == "TCP" or protocol == "UDP") and FLOW_TYPE == "AFLOW_OUT" :
            phase    = "MAINTAIN_ACCESS"
            addInfo2 = "destIP=" + dstip
        elif int(pkts) < 3 :		# downgrade to scan if number of packets is low - may need to tune this value
            phase    = "PROBING"    
            addInfo2 = "<3 pkts"
            
        # Update TSOM calculations    
        kojoney_attacker_event.generateAttackerEvent(txnId,attackerIP,p0fDict,sensorId,phase,eventSource,eventId,eventDesc,MD5,virusVendor,virusName,addInfo1,addInfo2)
        
        #Tweet if flow initiated by honeypot - this is interesting
        if phase == "MAINTAIN_ACCESS":
            return tweets
        else:    
            return None        

    except Exception,e:
        syslog.syslog("kojoney_argus_parse.py : processArgus() : " + `e` + " line=" + line)
        print "processArgus() : exception : " + e.__str__()
        return None

                               
# -------------------------------------------------------
        
# Start of code
# This is a test harness so comment/uncomment the relevent lines        
        
if __name__ == '__main__' :
       
# Set the input file to scan
    #filename = '/home/var/log/iplog.log'
    filename = '/home/var/log/argus.log'
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
            tweets = processArgus(222,"TEST",line)
            
        if tweets != None and len(tweets) != 0 :
            for tweet in tweets :
                print "*** Tweet : " + tweet
                       
        #print "sleeping..."
        # this can be a float for sub-second sleep    
        time.sleep(1)		# 0.1 
                              
                 