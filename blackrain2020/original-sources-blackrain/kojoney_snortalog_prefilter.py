#!/usr/bin/python

import syslog
import sys
import re

#BRX_IP   = "192.168.1.90"				# bug : read from a file in future
#BRAIN_IP = "192.168.1.67"
                                                                                                                                                                                                          
# does this break if there is not an Xref in the alert ?
# Jun 30 10:19:13 mars snort[6945]: [1:2100368:7] GPL ICMP_INFO PING BSDtype [Classification: Misc activity] [Priority: 3]: {ICMP} 192.168.1.240 -> 192.168.1.67
# Nov 11 16:28:37 192.168.1.5 snort[5907]: [1:2001219:18] ET SCAN Potential SSH Scan [Classification: Attempted Information Leak] [Priority: 2] <eth1> {TCP} 192.168.1.24
# Jul  6 22:24:02 mars snort[2401]: [1:2014384:8] ET DOS Microsoft Remote Desktop (RDP) Syn then Reset 30 Second DoS Attempt [Classification: Attempted Denial of Service] [Priority: 2]: {TCP} 72.14.163.130:52372 -> 192.168.1.60:3389
# Jun 30 14:13:36 mars snort[2395]: [116:58:1] (snort_decoder): Experimental Tcp Options found[Priority: 3]: {TCP} 195.246.49.33:38170 -> 192.168.1.60:3389
# move this to snort_funcs and make suricata use it 
def process(line):
  
    try:
        #print "kojoney_snortalog_prefilter.py : process() entered"
        #shorturl=""
        
        line = line.rstrip("\n")
        
        
        if "(portscan)" in line:
            return None

        if "(snort_decoder)" in line:
            return None
        
        if "(http_inspect)" in line:
            return None
        
        # Not as interesting as scans/attacks in the Snortalog Report
        if "ICMP" in line.upper():
            return None
        
        # Ermin DSL router
        if "192.168.1.10" in line:
            return None
        
        # Google DNS server
        if "8.8.8.8" in line:
            return None
        
        # WLAN used for testing 
        #if "192.168.1.180" in line:
        #    return None
        
        return line
        
    except Exception,e:
        msg = "kojoney_snortalog_prefilter.py : process() : " + e.__str__() + " line=" + line
        print msg
        syslog.syslog(msg)
                

if __name__ == '__main__' :
    
    #filename = '/home/var/log/suricata.syslog'
    #filename = '/home/var/log/shadow_ids.syslog'
    inFilename    = '/home/var/log/snort.syslog'
    outFilename   = '/usr/local/src/snortalog/snort_filtered.syslog'
    
    file  = open(inFilename,'r')
    fpOut = open(outFilename,'w')
    
    print "input file  : " + inFilename
    print "output file : " + outFilename
                
    while True:
        line  = file.readline() 
        
        if not line:
            print "No data to process, so exiting..."
            sys.exit(0)
        else:
            result = process(line)
            if result == None:
                print "Filtered out line : " + line
            else:
                #print "** Add to filtered Snort syslog file : " + line
                print >> fpOut,line
                    