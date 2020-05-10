#!/usr/bin/python

import syslog
import re
import ipintellib
                
if __name__ == '__main__' :
    
    filename = '/home/suricata/rules/tor.rules'
    file = open(filename,'r')

    total = 0	# total number of TOR IPs
                
    while True:
        line  = file.readline() 
        if not line :
            print "No more data to read"
            break
  
        #if "tcp" in line:
        torIP = re.findall("\d+\.\d+\.\d+\.\d+",line)
        if len(torIP) != 0 :
            for ip in torIP :
                total = total + 1
                    
                    #asInfo = ipintellib.ip2asn(ip)
                    #asNum = asInfo['as']                                               # AS123
                    #asRegisteredCode = asInfo['registeredCode']                     
                    #                  
                    #geoIP = ipintellib.geo_ip(ip)                    
                    #countryCode = geoIP['countryCode']
                    #
                    #print ip + " : " + countryCode.__str__() + " : " + asNum.__str__() + " : " + asRegisteredCode.__str__()
    
    # No more data in file to read    
    print "total number of TOR IPs : " + total.__str__()
    
        