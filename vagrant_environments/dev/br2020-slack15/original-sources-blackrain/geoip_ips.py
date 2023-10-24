#!/usr/bin/python

# Look for IPv4 addresses in the input file 
# Lookup information about the IP and write to stdout

import time
import os
import sys
import re 
import ipintellib

#filename    = '/home/var/log/geoip_test.txt'	# test file
#filename   = '/home/var/log/tweets.attempts.log.txt'
#filename   = '/home/var/log/honeyd.syslog'
#filename   = '/home/var/log/amun.syslog'
#outfilename = '/home/var/log/geoip-ipsX.results.txt'

filename    = sys.argv[1]
outfilename = sys.argv[2]

print "input  filename : " + filename
print "output filename : " + outfilename

file     = open(filename,'r')
outfile  = open(outfilename,'w')

uniqueIP    = {}
uniqueIntel = {}

while True:
        
    line  = file.readline().rstrip()
    if not line :
        print "input stream contains no more data to process, so exit."
        break
                    
    intel    = ""
    dnsName  = ""
    asMsg    = ""
    urlAsMsg = ""
    geoInfo  = ""
        
    # Look for IP address
    pat = r'\d+\.\d+\.\d+\.\d+'             # locate a number of IP addresses
    ips = re.findall(pat,line)  
    ip = None
    #print ips
    #print len(ips)
    if len(ips) != 0 :
        #print "first IP address found = " + `ips[0]`
        ip = ips[0]
   
        if uniqueIP.has_key(ip) != True :	# This IP has not been seen before
            #print ip
            uniqueIP[ip] = 1
    
            # Get DNS name
            dnsInfo = ipintellib.ip2name(ip)
            dnsName = dnsInfo['name'].rstrip('.')  
    
            # Get BGP AS info
            asMsg   = ipintellib.prettyAS(ip,',')                  
        
            # Get GeoIP information
            geoIP       = ipintellib.geo_ip(ip)
            countryCode = geoIP['countryCode']
            city        = geoIP['city']
            longitude   = geoIP['longitude']                                	# Used to calc approx. localtime
            latitude    = geoIP['latitude']
            region      = geoIP['region']
            geoInfo     = "cc=" + countryCode + "," + "region=" + region + "," + "city=" + city + "," + "lat=" + '%.2f' % latitude + "," + "long=" + '%.2f' % longitude             
              
            intel = ip + "," + "dns=" + dnsName + "," + asMsg + "," + geoInfo 
            uniqueIntel[ip] = intel      
            #print intel
                  
            
        else: 									# increment count for the IP
            uniqueIP[ip] = uniqueIP[ip] + 1 

# end of processing file             
# Print the list of IPs by number of events             
#print uniqueIP
print " "
for ip in uniqueIP :
    data = ip + "," + `uniqueIP[ip]` + "," + uniqueIntel[ip]
    #print data
    print >> outfile,data
                    