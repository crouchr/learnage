#!/usr/bin/python

import syslog
import re
import kojoney_snort_funcs

BRX_IP   = "192.168.1.90"				# bug : read from a file in future
BRAIN_IP = "192.168.1.67"
                                                                                                                                                                                                          
# does this break if there is not an Xref in the alert ?
# Jun 30 10:19:13 mars snort[6945]: [1:2100368:7] GPL ICMP_INFO PING BSDtype [Classification: Misc activity] [Priority: 3]: {ICMP} 192.168.1.240 -> 192.168.1.67
# Nov 11 16:28:37 192.168.1.5 snort[5907]: [1:2001219:18] ET SCAN Potential SSH Scan [Classification: Attempted Information Leak] [Priority: 2] <eth1> {TCP} 192.168.1.24
# Jul  6 22:24:02 mars snort[2401]: [1:2014384:8] ET DOS Microsoft Remote Desktop (RDP) Syn then Reset 30 Second DoS Attempt [Classification: Attempted Denial of Service] [Priority: 2]: {TCP} 72.14.163.130:52372 -> 192.168.1.60:3389
# Jun 30 14:13:36 mars snort[2395]: [116:58:1] (snort_decoder): Experimental Tcp Options found[Priority: 3]: {TCP} 195.246.49.33:38170 -> 192.168.1.60:3389
# move this to snort_funcs and make suricata use it 
def processSnmpSyslog(line):
  
    try:
        #print "kojoney_shadow_snort_parse.py : processSnortSyslog() entered"
        #shorturl=""
        srcIP     = "0.0.0.0"
        dstIP     = "192.168.1.68"
        protocol  = "UDP"
        oid       = "0"
        community = ""
        version   = "error"
                
        line = line.rstrip("\n")
        
        # Process authenticated SNMP requests only        
        if line.find("processIncomingMsg: looked up securityName ") >= 0 :                                                                                                                                                                     
            line   = line.rstrip('\n')       
            #print "----------------"                                                                                                                                                               
            #print line
        
            # Attacker IP
            pat = "\'(\d+\.\d+\.\d+\.\d+)\'"
            ips = re.findall(pat,line)
            if len(ips) > 0:
                srcIP = ips[0]
        
            # Community string
            pat = "communityName OctetString\(\'(.*)\'\)"
            a = re.findall(pat,line)
            if len(a) > 0:
                community = a[0]
            
            # Version
            pat = "securityModel (\d+)"
            a = re.findall(pat,line)
            if len(a) > 0:
                version = a[0]

            msg = "SNMP REQ community=" + community + " version=" + version
            msg = '[' + msg + ']'
            #print '[' + msg + ']'
        
            # compose the tweet
            tweet = srcIP + " -> " + dstIP + " " + protocol + " " + msg          
            tweet = kojoney_snort_funcs.snortTwittifyLite(tweet)
            tweet = "SNMP_HIDS," + tweet
            return tweet
            
        #elif line.find("name=1.3") >= 0 :                                                                                                                                                                     
        elif line.find("readGet: ") >= 0 :                                                                                                                                                                     
            line   = line.rstrip('\n')       
            #print "----------------"                                                                                                                                                               
            #print line
            msg = line.replace("DBG:","")
            msg = msg.replace(", ",".")
            msg = msg.replace(" readGet","OID")
            #print msg
            #msg = "community=" + community + " version=" + version
            msg = '[' + msg + ']'
            #print '[' + msg + ']'
        
            # compose the tweet
            #tweet = srcIP + " -> " + dstIP + " " + protocol + " " + msg          
            #tweet = kojoney_snort_funcs.snortTwittifyLite(tweet)
            tweet = "SNMP_HIDS," + msg
            return tweet
            
    except Exception,e:
        msg = "kojoney_snmp_parse.py : processSnmpSyslog() : " + `e` + " line=" + line
        print msg
        syslog.syslog(msg)
                
if __name__ == '__main__' :
    
    filename = '/home/var/log/kojoney_snmp_hpot.log'
    
    file = open(filename,'r')
                
    while True:
        line  = file.readline() 
        tweet = processSnmpSyslog(line)
        
        if tweet != None:
            print "tweet:" + tweet
        
        