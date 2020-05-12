#!/usr/bin/python

import syslog
import kojoney_bitly
import getURLghetto

import kojoney_snort_funcs
import kojoney_defend

import getSnortInfo

BRX_IP   = "192.168.1.90"				# bug : read from a file in future
BRAIN_IP = "192.168.1.67"
                                                                                                                                                                                                          
# does this break if there is not an Xref in the alert ?
#Feb 17 21:10:31 mars kernel[152] SID1768 ESTAB IN=eth0 OUT= MAC=00:0c:29:a1:dd:89:00:14:bf:77:42:b8:08:00 SRC=207.171.3.142 DST=192.168.1.62 LEN=52 TOS=0x00 PREC=0x00 TTL=47 ID=33003 DF PROTO=TCP SPT=48755 DPT=18080 WINDOW=46 RES=0x00 ACK URGP=0 OPT (0101080A0E17BBEC002AC393) 
#Feb 17 21:10:31 mars kernel[152] SID1768 ESTAB IN=eth0 OUT= MAC=00:0c:29:a1:dd:89:00:14:bf:77:42:b8:08:00 SRC=207.171.3.142 DST=192.168.1.62 LEN=202 TOS=0x00 PREC=0x00 TTL=47 ID=33004 DF PROTO=TCP SPT=48755 DPT=18080 WINDOW=46 RES=0x00 ACK PSH URGP=0 OPT (0101080A0E17BBEC002AC393) 
#Feb 17 21:10:31 mars kernel[2497] SID2013116 ESTAB IN=eth0 OUT= MAC=00:0c:29:a1:dd:89:00:14:bf:77:42:b8:08:00 SRC=207.171.3.142 DST=192.168.1.62 LEN=202 TOS=0x00 PREC=0x00 TTL=47 ID=33004 DF PROTO=TCP SPT=48755 DPT=18080 WINDOW=46 RES=0x00 ACK PSH URGP=0 OPT (0101080A0E17BBEC002AC393) 
#Feb 17 21:10:33 mars kernel[152] SID1768 ESTAB IN=eth0 OUT= MAC=00:0c:29:a1:dd:89:00:14:bf:77:42:b8:08:00 SRC=207.171.3.142 DST=192.168.1.62 LEN=202 TOS=0x00 PREC=0x00 TTL=47 ID=13464 DF PROTO=TCP SPT=49786 DPT=18080 WINDOW=46 RES=0x00 ACK PSH URGP=0 OPT (0101080A0E17C4D5002AC5B7) 
#Feb 17 21:10:33 mars kernel[2497] SID2013116 ESTAB IN=eth0 OUT= MAC=00:0c:29:a1:dd:89:00:14:bf:77:42:b8:08:00 SRC=207.171.3.142 DST=192.168.1.62 LEN=202 TOS=0x00 PREC=0x00 TTL=47 ID=13464 DF PROTO=TCP SPT=49786 DPT=18080 WINDOW=46 RES=0x00 ACK PSH URGP=0 OPT (0101080A0E17C4D5002AC5B7) 
#Feb 17 21:10:34 mars kernel[9682] SID1087 ESTAB IN=eth0 OUT= MAC=00:0c:29:a1:dd:89:00:14:bf:77:42:b8:08:00 SRC=207.171.3.142 DST=192.168.1.62 LEN=52 TOS=0x00 PREC=0x00 TTL=47 ID=13467 DF PROTO=TCP SPT=49786 DPT=18080 WINDOW=96 RES=0x00 ACK URGP=0 OPT (0101080A0E17C8C9002AC6DE) 
#Feb 17 21:10:36 mars kernel[152] SID1768 ESTAB IN=eth0 OUT= MAC=00:0c:29:a1:dd:89:00:14:bf:77:42:b8:08:00 SRC=207.171.3.142 DST=192.168.1.62 LEN=194 TOS=0x00 PREC=0x00 TTL=47 ID=28784 DF PROTO=TCP SPT=50810 DPT=18080 WINDOW=46 RES=0x00 ACK PSH URGP=0 OPT (0101080A0E17CEA9002AC7FD) 
def processFwSnortSyslog(line):
  
    try:
        shorturl=""
        
        line = line.rstrip("\n")
        
        # Do not want any event associated with the active scanning of the Blackrain sensor itself
        if line.find(BRAIN_IP) != -1 :
            #msg = "IDS event associated with BRAIN sensor ip=" + BRAIN_IP + " itself , so ignore  " + line
            #print msg
            #syslog.syslog(msg)
            return None
        
        # Polluted syslog file so ignore
        if line.find("] SID") == -1 :
            return None
       
        a = line.find("SRC=")           # source IP
        #b = line.find("SPT=")           # source port
        c = line.find("DST=")           # destination IP
        #d = line.find("DPT=")           # dest port
        e = line.find("PROTO=")         # TCP UDP
        #f = line.find("TTL=")           # TTL for OS fingerprinting compared to p0f
        #g = line.find("ID=")            # IP ID
        h = line.find("SID")            # FWSnort signature
        #i = line.find("DRP")            # Traffic was dropped
                                                                        
        # flow1 - mandatory flow info
        srcIP   = line[a:].split(" ")[0].split("=")[1]
        #srcPort = line[b:].split(" ")[0].split("=")[1]
        dstIP   = line[c:].split(" ")[0].split("=")[1]    
        #dstPort = line[d:].split(" ")[0].split("=")[1]
        proto   = line[e:].split(" ")[0].split("=")[1]
 
         # flow2 - additional flow info 
        #ttl     = line[f:].split(" ")[0].split("=")[1]
        #ipid    = line[g:].split(" ")[0].split("=")[1]
        sid     = line[h:].split(" ")[0] 
        sid     = sid[3:]               # ignore the "SID" on the front
                                                     
       # does line contain uninteresting / duplicate Snort alert
        sidNormal = "NIDS_SU snort[:" + sid + ":] Classification" 	# match routine has ":" bookends
        #print "sidNormal=" + sidNormal
        if kojoney_snort_funcs.suppressSnortAlert(sidNormal) == True :
            print "ignore -> " + line
            return
        

        
        # remove Don't Fragment Flag from message - mucks up parsing     
        #line = line.replace(" DF ","")            
                                                                                                                                                               
        # strip off date and unwanted syslog pre-messages
        #fields = line.split(" ")
        #print fields
        
        #sPort = ""
        #dPort = ""
        #sid   = fields[5]
        
        #if line.find("ESTAB") != -1 :
        #    srcIP = fields[10]
        #    dstIP = fields[11]
        #    proto = fields[16]
        #    sPort = fields[17]
        #    dPort = fields[18] 
        #else:
        #    srcIP = fields[9]
        #    dstIP = fields[10]
        #    proto = fields[15]
        #    if line.find("UDP") != -1 :
        #        sPort = fields[16]
        #        dPort = fields[17]
        
        #snortMsg = "sid=" + sid + ",ev=" + getSnortInfo.getFwsnortMsg(sid) + ",ct=" + getSnortInfo.getFwsnortAtom(sid,"classtype") + ",ref=" + getSnortInfo.getFwsnortAtom(sid,"reference")            
        
        tweet = "[:" + sid + ":]" + " " + getSnortInfo.getFwsnortMsg(sid) + " " + proto + " " + srcIP +  "->" + dstIP 
        # tweet = tweet.replace("  "," ")	# ICMP has double spaces due to no ports
        
        tweet = kojoney_snort_funcs.snortTwittify(tweet)

        tweet = "FW_SNORT," + tweet

        # active response if snort detects brute force attacks - these probably don't result in malware download
        #if line.find(" brute ") != -1 or line.find(" Brute ") != -1 or line.find("bruteforce") != -1 or line.find("port 1433") != -1 or line.find("SIPvicious scan ") != -1 or line.find("SNMP Scan") != -1 :
        if line.find("bruteforce") != -1 or line.find("scan") != -1 or line.find("Scan") != -1 :
            bh_tweet = kojoney_defend.blackhole(srcIP)
        else:
            bh_tweet = None
                                            
        # construct return list of tweets
        tweets = []
        tweets.append(tweet)   
        
        if bh_tweet != None:
            tweets.append(bh_tweet)
            
        return tweets
        
    except Exception,e:
        msg = "kojoney_fwsnort_parse.py : processFwSnortSyslog() : " + `e` + " line=" + line
        print msg
        syslog.syslog(msg)
                

if __name__ == '__main__' :
    
    filename = '/home/var/log/fwsnort.syslog'
    file = open(filename,'r')
                
    while True:
        line  = file.readline() 
        tweet = processFwSnortSyslog(line)
        
        if tweet != None:
            print "tweet:" + tweet
        
        