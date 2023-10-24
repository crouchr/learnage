#!/usr/bin/python

import os,logging,re 
import syslog
#Starting Nmap 4.65 ( http://nmap.org ) at 2011-06-07 05:57 BST
#Interesting ports on 58.42.32.159:
#PORT    STATE    SERVICE
#135/tcp open     msrpc
#139/tcp open     netbios-ssn
#445/tcp filtered microsoft-ds
#
#Nmap done: 1 IP address (1 host up) scanned in 3.445 seconds
#

#No exact OS matches for host (test conditions non-ideal).
#Uptime guess: 367.845 days (since Thu Oct 28 11:07:28 2010)
#Network Distance: 26 hops
#TCP Sequence Prediction: Difficulty=200 (Good luck!)
#IP ID Sequence Generation: All zeros
#
# -F = just scan top 100 most popular open ports

def xprobeScan(ip): 
    try:
        
        #cmdLine = "/usr/local/bin/nmap -P0 -O -v " + ip
        # -p1-65535
        cmdLine = "/usr/local/bin/xprobe2 " + ip + " > /home/var/log/scans/" + "xprobe-" + ip + ".txt"
        print cmdLine
        
        syslog.syslog("started: " + cmdLine)
        pipe = os.popen(cmdLine,'r')
        raw = pipe.read()
        syslog.syslog("finished: " + cmdLine)
      
        print "raw=",raw
        #openPorts     = re.findall("(\d+)\/tcp\s+open",raw)
        #filteredPorts = re.findall("(\d+)\/tcp\s+filtered",raw)
 
        # TTL hops
        #hops = None
        #if raw.find("Network Distance: ") != -1:
        #    hops = re.findall("Network Distance: (\d+)",raw)
        #    hops = hops[0].__str__()
            #print "hops = " + hops
            
        # Operating System    
        #osService = "?"
        #if raw.find("OS:") != -1 :
        #    osService = re.findall("OS: (\w+)",raw)
        #    if len(osService) == 1 :
        #        osService = osService[0]
        #    else:
        #        osService = "?"    
        #print osService

        # Service info : hostname  
        # Service Info: Host: psyBNC.at; OS: Unix  
        # bug -> can handle the '.' characters
        #hostname = "?"
        #if raw.find("Host: ") != -1 :
        #    hostname = re.findall("Host: (\w+)",raw)
        #    if len(hostname) == 1 :
        #        hostname = hostname[0]
        #    else:
        #        hostname = "?"    
        #print hostname 

        # Uptime (not Windows)    
        #uptime = "?"
        #if raw.find("Uptime guess:") != -1 :
        #    print "Located Uptime guess: in nmap output"
        #    uptime = re.findall("Uptime guess: (\d+)\.\d+ (\w+) ",raw)
        #    if len(uptime) == 1 :
        #        uptimeVal,uptimeUnits = uptime[0]	# unpack the tuple returned
        #        uptime = uptimeVal + " " + uptimeUnits
        #    else:
        #        uptime = "?"    
        #print uptime

        # IP ID 
        #ipid = "?"
        #if raw.find("IP ID Sequence Generation:") != -1 :
        #    print "Located IP ID in nmap output"
        #    ipid = re.findall("IP ID Sequence Generation: (.+)",raw)
        #    if len(ipid) == 1 :
        #        ipid = ipid[0]	# unpack the tuple returned
        #        if ipid.find("Busy server or unknown class") != -1 :
        #            ipid = "unknown"
        #    else:
        #        ipid = "?"    
        #print ipid

        # TCP Sequnece number prediction - ISN - vulnerable to TCP spoofing
        #tcpSeq = "?"
        #if raw.find("TCP Sequence Prediction:") != -1:
        #    print "Located TCP Sequence Prediction in nmap output"
        #    tcpSeq = re.findall("TCP Sequence Prediction: (.+)",raw)
        #if len(tcpSeq) == 1 :
        #    tcpSeq = tcpSeq[0]
        #    tcpSeq = tcpSeq.replace(" (Good luck!)","")	# not very interesting in a Tweet
        #else:
        #    tcpSeq = "?"
      
        # return results
        #return openPorts,filteredPorts,hops,osService,uptime,ipid,tcpSeq,hostname
    
    except Exception,e:
        msg = "kojoney_xprobe.py : " + e.__str__() 
        print msg
        syslog.syslog(msg)


#root@cloud:/usr/local/etc/unicornscan#  nmap -sUV -p111,5060,161,53,987 192.168.1.67   
#
#Starting Nmap 5.51 ( http://nmap.org ) at 2011-11-01 07:04 GMT
#Nmap scan report for 192.168.1.67
#Host is up (0.13s latency).
#PORT     STATE  SERVICE VERSION
#53/udp   open   domain  dnsmasq 2.45
#111/udp  closed rpcbind
#161/udp  closed snmp
#987/udp  closed unknown
#5060/udp closed sip
#MAC Address: 00:0C:29:A1:DD:89 (VMware)
#
#Service detection performed. Please report any incorrect results at http://nmap.org/submit/ .
#Nmap done: 1 IP address (1 host up) scanned in 2.78 seconds

                
if __name__ == '__main__' :

    #openPorts,filteredPorts = nmapScan("58.42.32.159")
    #openPorts,filteredPorts = nmapScan("217.42.192.41")
    #openPorts,filteredPorts,hops,os = nmapScan("60.10.179.100")
    #\ slackware - no Service detection
    #openPorts,filteredPorts,hops,os = nmapScan("204.246.0.134")
    
    # BR Linux
    #openPorts,filteredPorts,hops,os,uptime,ipid = nmapScan("187.61.61.235")
 
    # TW
    #openPorts,filteredPorts,hops,os,uptime,ipid,tcpSeq = nmapScan("211.74.113.79")    

    # ??
    #openPorts,filteredPorts,hops,os,uptime,ipid,tcpSeq,hostname = nmapScan("41.223.85.14")    

    # IP ID - busy server or unknown class
    #openPorts,filteredPorts,hops,os,uptime,ipid,tcpSeq,hostname = nmapScan("88.87.21.102")    
    result = xprobeScan("41.223.85.14")
    
    #print "open               : " + openPorts.__str__()
    #print "filtered           : " + filteredPorts.__str__()
    #print "os (Service)       : " + os.__str__()
    #print "hops               : " + hops.__str__()
    #print "uptime             : " + uptime.__str__()
    #print "IP ID              : " + ipid.__str__()
    #print "TCP Seq predict    : " + tcpSeq.__str__()
    #print "hostname (Service) : " + hostname.__str__()
                                                                               