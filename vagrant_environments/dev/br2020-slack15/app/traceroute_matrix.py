#!/usr/bin/python

# call with ./traceroute-matrix.p /home/var/log/p0f.log
# works with any file containing source IPs as the first IP in the file

import sys,os
import syslog
import re
import fileinput
import ipintellib
import kojoney_nmap


# master is on mars
# exception handling needs to be added i.e. log to syslog

# traceroute to an IP address and gather list of AS in the path
def traceroute(sensorId,ip,hops,fpDebug=None):
     asn = []
     asnUnique = []
     
     print "----------------------"
     if fpDebug != None:
         print >> fpDebug,"-------------"
     
     if hops != 0:
         #cmdLine = "/usr/local/bin/traceroute -p 53 -A -m " + hops.__str__() + " " + ip
         cmdLine = "/usr/local/bin/paris-traceroute -n -m " + hops.__str__() + " " + ip
     else:
         #cmdLine = "/usr/local/bin/traceroute -p 53 -A " + ip
         cmdLine = "/usr/local/bin/traceroute -n " + ip  
     print cmdLine    

     pipe = os.popen(cmdLine,'r')
     if pipe == None :
         syslog.syslog("getP0fInfo() os.popen() returned None for " + cmdLine)
     raw = pipe.read().strip()
     if fpDebug != None:
         print >> fpDebug,raw
     print "raw = " + raw.__str__()                                  

     #asn = re.findall("AS(\d+)",raw)
     ipList = re.findall("(\d+\.\d+\.\d+\.\d+)",raw)
     print "traceroute() : list of IPs = " + ipList.__str__()

     for ip in ipList[3:] :
         a = ipintellib.ip2asn(ip)    
         #asn.append(a['as'] + ":" + a['registeredCode'])
         asn.append(a['registeredCode'])
     
     print "asn = " + asn.__str__()    
     #sys.exit()

     # Pre-pend sensorId to start of AS Path
     asnUnique.append(sensorId)
     asnUnique = asnUnique + asn
     # Create list of unique AS numbers by filtering out duplicates
     # asnUnique.append("AS" + asn[0])
     #for i in range(0,len(asn)-1):
     #     if asn[i+1] != asn[i] :
     #          if asn[i+1] != "28513" and asn[i+1] != "8151":	# IP is private IP ?
     #              asnUnique.append("AS" + asn[i+1])
     
     # Append the countryCode to the target IP
     geoIP = ipintellib.geo_ip(ip)
     countryCode = geoIP['countryCode']        
     city        = geoIP['city']                             
     #asnUnique.append(countryCode.__str__() + ":" + ip + ":" + city.__str__())
     asnUnique.append(countryCode.__str__() + ":" + ip)
     
     # Eliminate duplicates
     asnUnique = eliminateASpathDuplicates(asnUnique)
     print asnUnique                
     if fpDebug != None:
         print >> fpDebug,"traceroute(out) : " + asnUnique.__str__()
     
     return asnUnique


# Create list of unique AS numbers by filtering out duplicates
     # asnUnique.append("AS" + asn[0])
def eliminateASpathDuplicates(asPath):
    asnUnique = []
    
    a = len(asPath)
    print a
    asnUnique.append(asPath[0])				# restore HPOT tag
    
    print "eliminateASpathDuplicates() : asPath raw     : " + asPath.__str__()
    for i in range(0,len(asPath)-2):
        if asPath[i+1] != asPath[i] :
            if asPath[i+1] != "28513" and asPath[i+1] != "8151":	# IP is private IP ?
                asnUnique.append(asPath[i+1])
    
    asnUnique.append(asPath[a-1])			# restore attacker IP and CC            
    
    print "eliminateASpathDuplicates() : asPath cleaned : " + asnUnique.__str__()
    return asnUnique 


# input asPath := ['666666666666', 'AS1234', 'AS4567', 'AS2856', 'CN:124.105.166.228']
# only keep the outer 2 AS numbers
# not sure if this is actually used at the moment
def removeCore(asPath):
    a = []
    b = len(asPath)
    print "removeCore() : asPath=" + asPath.__str__()
    
    
    a.append(asPath[0])				# Honeypot sensorID
    a.append(asPath[1])				# Honeypot sensor AS
    a.append("INTERNET_CORE")
    if b >= 5 :
         a.append(asPath[len(asPath)-3])     	# Attacker AS
         print "b=" + b.__str__()
    a.append(asPath[len(asPath)-2])     	# Attacker AS 
    a.append(asPath[len(asPath)-1])		# Attacker IP address
    
    return a
    
# write AfterGlow-compatible list of source and destinations to file 
# input asPath := ['666666666666', 'AS1234', 'AS4567', 'AS2856', 'CN:124.105.166.228']
# output file  := 
# 666666666666,AS1234
# AS1234,AS4567
# AS4567,AS2856
# CN:124.105.166.228
def afterglow(asPath,fpOut,fpDebug):
    print "afterglow() : asPath = " + asPath.__str__()
    
    # Write the AS Path info to debug file
    print >> fpDebug,"afterglow(in) : " + asPath.__str__()
       
    for i in range(0,len(asPath)-1):
        #print asPath[i]
        a = asPath[i] + "," + asPath[i+1]
        print >> fpOut,a    
        print >> fpDebug,a
        print a
    
    return None 

# append AfterGlow-compatible list of attacker IP and open TCP ports to file 
def afterglowPorts(ip,openPorts,fpOut,fpDebug):
    a = "afterglowPorts() : openPorts = " + openPorts.__str__()
    print a
    print >> fpDebug,a
    
    geoIP = ipintellib.geo_ip(ip)
    countryCode = geoIP['countryCode']        
    city        = geoIP['city']                             
    #attacker = countryCode.__str__() + ":" + ip + ":" + city.__str__()
    attacker = countryCode.__str__() + ":" + ip
    
    # Write open ports info to afterglow file   
    for i in openPorts:
        a = i.__str__() + "," + attacker
        print >> fpOut,a    
        print >> fpDebug,a
        print a
    
    return None 


def main(argv):

    syslog.openlog("traceroute_matrix")
        
    #hops = 10
    hops = 35
    
    #print argv[0]
    a = len(argv)
    #print a

    attackers = []
    ipHash = {}
    
    # test code
    #asPath = ['HPOT','123','8151','234','234','234','345','CN:6.6.6.6']
    #a = eliminateASpathDuplicates(asPath)
    #print a
    
    # If a command-line parameter is present, it is a file of IP addresses
    # Populate the list called attackers with all the unique IPs in the file
    # [('111.240.241.198', '56615'), ('192.168.1.62', '18080')]

    if a == 2 :
        #fpIn = open(argv[1],"r")
        for line in fileinput.input(argv[1]):
            ip = re.findall("(\d+\.\d+\.\d+\.\d+)\:(\d+)",line)
            if len(ip) != 0 :
                #print ip
                srcIP   = ip[0][0]
                srcPort = ip[0][1]
                dstIP   = ip[1][0]
                dstPort = ip[1][1]
                #print "srcIP=" + srcIP + " dstPort=" + dstPort
                if ipHash.has_key(srcIP) != True and not "192.168.1." in srcIP :
                    # Does the destination port indicate an exploit ?
                    if dstPort == "135" or dstPort == "137" or dstPort == "139" or dstPort == "445" or dstPort == "1025" or dstPort == "2967" or dstPort == "1433" or dstPort == "5554" :
                        print "botnet drone : srcIP=" + srcIP + " dstPort=" + dstPort
                        ipHash[srcIP] = 1
                        attackers.append(srcIP)
                    
    print "Number of unique attacker IPs found = " + len(attackers).__str__()
    print " "
    print attackers
    print " "
        
    sensorId = "666666666666"
    sensorId = "s:ermin"
    sensorId = "HONEYPOT"

    #attackers = ['88.240.134.128','111.240.241.198','67.205.111.245','202.85.222.199','184.22.223.190','222.241.150.4','41.233.138.24','184.95.37.124']

    fpOut   = open("/home/var/secviz/aspath.csv","w")
    fpDebug = open("/home/var/secviz/aspath-debug.txt","w")
        
    #target = sys.argv[1]
    #print target
    syslog.syslog("Started traceroute scan to " + len(attackers).__str__() + " attacker IPs, max hops=" + hops.__str__() + "...")
    for ip in attackers:
         a = traceroute(sensorId,ip,hops,fpDebug)		
         print "AsPath = " + a.__str__()
         
         #a = removeCore(a)
         #print "AsPath(Core Removed) = " + a.__str__()
         
         afterglow(a,fpOut,fpDebug)
         
         # nmap scan the attacker, but only if a "safe" country
         #geoIP = ipintellib.geo_ip(ip)
         #countryCode = geoIP['countryCode']        
         #print countryCode
         #if countryCode != "GB" and countryCode != "DE":
         #    openPorts,filteredPorts = kojoney_nmap.nmapScan(ip)
         #    if openPorts != None :
         #        print openPorts
         #        afterglowPorts(ip,openPorts,fpOut,fpDebug)
         #else:
         #    print "Skipping " + ip + ", it is based in " + countryCode + " !"    
               
    fpOut.close()
    syslog.syslog("Finished traceroute scan to " + len(attackers).__str__() + " attacker IPs")
    
# tshark -i br0 -n 'not port 53 and (udp or icmp)'


if __name__ == '__main__' :
     main(sys.argv)
