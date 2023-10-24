#!/usr/bin/python

import syslog
import kojoney_bitly
import getURLghetto
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
def processSnortSyslog(line):
  
    try:
        #print "kojoney_shadow_snort_parse.py : processSnortSyslog() entered"
        shorturl=""
        
        line = line.rstrip("\n")
        
        #print "-----------------------"
        #print line
        
        # Do not want any event associated with the active scanning of the Blackrain sensor itself
        #if line.find(BRAIN_IP) != -1 :
        #    msg = "IDS event associated with BRAIN sensor ip=" + BRAIN_IP + " itself , so ignore  " + line
        #    print msg
        #    syslog.syslog(msg)
        #    return None
        
        # does line contain uninteresting / duplicate Snort alert
        if kojoney_snort_funcs.suppressSnortAlert(line) == True :
            #print "*** Suppress boring Snort event"
            return
                                                                                                                                                             
        #line   = line.rstrip('\n')       
        #print "----------------"                                                                                                                                                               
        #print line
        
        # SID and SID-origin
        pat = "\[\d+\:(\d+)\:\d+\]" 
        sid = re.findall(pat,line)
        if len(sid) > 0 :
            #print sid
            sid       = sid[0]
            #sidOrigin = sid[0][1]
            #print "sid=" + sid.__str__() + " sidOrigin=" + sidOrigin.__str__()
        else:
            sid = "0"
  
        # protocol
        pat = "\{(.*)\}"
        protocol = re.findall(pat,line)
        if len(protocol) > 0:
            protocol = protocol[0]
        else:
            protocol = "-"
          
        # ICMP
        if protocol == "ICMP":
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
            pat = "(\d+\.\d+\.\d+\.\d+)\:(\d+) -> (\d+\.\d+\.\d+\.\d+)\:(\d+)" 
            ips = re.findall(pat,line)
            if len(ips) > 0:
                #print ips
                srcIP   = ips[0][0]
                srcPort = ips[0][1]
                dstIP   = ips[0][2]
                dstPort = ips[0][3]
                #print "TCP/UDP : " + srcIP + ":" + srcPort + " -> " + dstIP + ":" + dstPort

        # priority
        pat = "Priority: (\d+)"
        priority = re.findall(pat,line)
        if len(priority) > 0:
            priority = priority[0]
        else:
            #priority = "-1"
            priority = "9"	# Will be ignored by priority check later in this function
            
        #print "priority = " + priority
        
        # Ignore priority level 3 and above
        if int(priority) > 2 :
            #print "*** Ignore low priority Snort event ***"
            return None
        
        # Classification
        if "Classification" in line:
            pat = "Classification: (.*)\] "
            classification = re.findall(pat,line)
            if len(classification) > 0 :
                classification = classification[0]
            else:
                classification = "-"
        #print "classification = " + classification

        # Snort Rule Message
        msg = "-"
        if classification != "-":
            pat = "\] (.*) \[Classification"
            msg = re.findall(pat,line)
            if len(msg) > 0:
                msg = msg[0]
                msg = msg.lstrip(" ")
                msg = msg.rstrip(" ")
            else:
                msg = "-"
        # Jun 30 14:13:36 mars snort[2395]: [116:58:1] (snort_decoder): Experimental Tcp Options found[Priority: 3]: {TCP} 195.246.49.33:38170 -> 192.168.1.60:3389
        else:
            pat = "\):(.*)\[Priority"    
            msg = re.findall(pat,line)
            if len(msg) > 0:
                msg = msg[0]
                msg = msg.lstrip(" ")
                msg = msg.rstrip(" ")
                msg = "preproc:" + msg
            else:
                msg = "-"                
        #print "msg = " + msg

        # compose the tweet
        if protocol == "ICMP":
            tweet = srcIP + " -> " + dstIP + " " + protocol + " " + "P" + priority + " [" + "SID=" + sid + " " + msg + ']'  
        else:
            # Source Port is not interesting enough -> save space in Tweet
            tweet = srcIP + " -> " + dstIP + ":" + dstPort + " " + protocol + " [" + "P" + priority + " " + "SID=" + sid + " " + msg + ']'  
                    
        
        tweet = kojoney_snort_funcs.snortTwittify(tweet)
        #tweet = kojoney_snort_funcs.snortTwittifyLite(tweet)

        #tweet = "NIDS_SH," + tweet
        tweet = "SNORT_NIDS," + tweet
         
        return tweet
        
    except Exception,e:
        msg = "kojoney_shadow_parse.py : processSnortSyslog() : " + `e` + " line=" + line
        print msg
        syslog.syslog(msg)
                

if __name__ == '__main__' :
    
    #filename = '/home/var/log/suricata.syslog'
    #filename = '/home/var/log/shadow_ids.syslog'
    filename = '/home/var/log/snort.syslog'

    file = open(filename,'r')
                
    while True:
        line  = file.readline() 
        tweet = processSnortSyslog(line)
        
        if tweet != None:
            print "**** tweet=[" + tweet + "]"
        
   