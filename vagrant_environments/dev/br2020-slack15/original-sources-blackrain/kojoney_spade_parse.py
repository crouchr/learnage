#!/usr/bin/python

import syslog
#import kojoney_bitly
#import getURLghetto
import re
import kojoney_snort_funcs
import kojoney_hiddenip

BRX_IP   = "192.168.1.90"				# bug : read from a file in future
BRAIN_IP = "192.168.1.67"
                                                                                                                                                                                                          
# does this break if there is not an Xref in the alert ?
# Jun 30 10:19:13 mars snort[6945]: [1:2100368:7] GPL ICMP_INFO PING BSDtype [Classification: Misc activity] [Priority: 3]: {ICMP} 192.168.1.240 -> 192.168.1.67
# Nov 11 16:28:37 192.168.1.5 snort[5907]: [1:2001219:18] ET SCAN Potential SSH Scan [Classification: Attempted Information Leak] [Priority: 2] <eth1> {TCP} 192.168.1.24
# Jul  6 22:24:02 mars snort[2401]: [1:2014384:8] ET DOS Microsoft Remote Desktop (RDP) Syn then Reset 30 Second DoS Attempt [Classification: Attempted Denial of Service] [Priority: 2]: {TCP} 72.14.163.130:52372 -> 192.168.1.60:3389
# Jun 30 14:13:36 mars snort[2395]: [116:58:1] (snort_decoder): Experimental Tcp Options found[Priority: 3]: {TCP} 195.246.49.33:38170 -> 192.168.1.60:3389
# move this to snort_funcs and make suricata use it 
def processSpadeSyslog(line):
  
    try:
        #print "kojoney_shadow_snort_parse.py : processSnortSyslog() entered"
        #shorturl=""
        
        line = line.rstrip("\n")
        
        # Just for the moment, disable tweeting for this sensor - need to eliminate false positives first
        # Parsing code works fine
        return None
                
        if line.find("last message repeated") >= 0 :	# ignore this syslog message	
            return
        
        if line.find("Spade: ") < 0 :
            return
            
        if line.find("teardown flags") >= 0 :	# false positives - unknown reason but ignore for now	
            return
                                                                                                                                                                     
        line   = line.rstrip('\n')       
        #print "----------------"                                                                                                                                                               
        #print line
        
        # SID and SID-origin
        #pat = "\[\d+\:(\d+)\:\d+\]" 
        #sid = re.findall(pat,line)
        #if len(sid) > 0 :
        #    #print sid
        #    sid       = sid[0]
        #    #sidOrigin = sid[0][1]
        #    #print "sid=" + sid.__str__() + " sidOrigin=" + sidOrigin.__str__()
        #else:
        #    sid = "0"
  
        # protocol
        pat = "\{(.*)\}"
        protocol = re.findall(pat,line)
        if len(protocol) > 0:
            protocol = protocol[0]
        else:
            protocol = "-"
          
        # ICMP
        if protocol == "ICMP":
            #print "ICMP"
            pat = "(\d+\.\d+\.\d+\.\d+) -> (\d+\.\d+\.\d+\.\d+)" 
            ips = re.findall(pat,line)
            if len(ips) > 0:
                #print ips
                srcIP   = ips[0][0]
                srcPort = "-1"
                dstIP   = ips[0][1]
                dstPort = "-1"
                #print "ICMP : " + srcIP + ":" + srcPort + " -> " + dstIP + ":" + dstPort
        else: # UDP/TCP etc
            #print "TCP/UDP"
            pat = "(\d+\.\d+\.\d+\.\d+)\:(\d+) -> (\d+\.\d+\.\d+\.\d+)\:(\d+)" 
            ips = re.findall(pat,line)
            if len(ips) > 0:
                #print ips
                srcIP   = ips[0][0]
                srcPort = ips[0][1]
                dstIP   = ips[0][2]
                dstPort = ips[0][3]
                #print "TCP/UDP : " + srcIP + ":" + srcPort + " -> " + dstIP + ":" + dstPort
        
        msg = line.split("Spade: ")[1]
        msg = msg.split('{')[0].rstrip(" ")
        
        msg = msg.replace("syn:","SYN:")
        msg = msg.replace("synack:","SYNACK:")
        msg = msg.replace("est. flags:","ESTABLISHED:")
        
        
        msg = '[' + msg + ']'
        #print '[' + msg + ']'
        
        # compose the tweet
        if protocol == "ICMP":
            tweet = srcIP + " -> " + dstIP + " " + protocol + " " + msg  
        else:
            tweet = srcIP + ":" + srcPort + " -> " + dstIP + ":" + dstPort + " " + protocol + " " + msg   
                    
        tweet = kojoney_snort_funcs.snortTwittifyLite(tweet)

        tweet = "SPADE_ADS," + tweet

        # Do not return Tweet if the srcIP is on whitelist
        ipList = []
        ipList.append(srcIP)
        ipList.append(dstIP)
        print "Candidate tweet: " + tweet
        print "*** kojoney_spade_parse.py : calling hiddenIP() ***" 
        if kojoney_hiddenip.hiddenIP(ipList) == True:
            return None 
         
        return tweet
        
    except Exception,e:
        msg = "kojoney_spade_parse.py : processSpadeSyslog() : " + `e` + " line=" + line
        print msg
        syslog.syslog(msg)
                

if __name__ == '__main__' :
    
    filename = '/home/var/log/spade.syslog'
    
    file = open(filename,'r')
                
    while True:
        #print "----------------"
        line  = file.readline() 
        #print line.rstrip()
        tweet = processSpadeSyslog(line)
        
        if tweet != None:
            print "*** Send tweet:" + tweet
        