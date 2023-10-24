#!/usr/bin/python

# This is the definitive function as a library


import os
import sys, syslog

import ipintellib	

def test():
    print "\n\n\n\n"
    print "=========================="
    print "p0f logfile to Reputation "
    print "=========================="
    print "Library version : " + ipintellib.getVersion()

    print "Hard-coded tests"
    print "----------------"
    # IP to DNS name
    ipStr = "217.41.27.169"			# My IP
    dnsInfo  = ipintellib.ip2name(ipStr)	        	# resolve get DNS name	
    print ipStr + " resolves to " + dnsInfo['name']

    # DNS name to IP
    ipStr = "www.openbsd.org"
    dnsInfo  = ipintellib.ip2name(ipStr)	        	# resolve get DNS name	
    print ipStr + " resolves to " + dnsInfo['name']
    
    # input file : file of IPs (hand-crafted)
    fpIn   = open(r'/home/var/log/p0f.log','r')

    # output file 
    fpOut0 = open(r'/home/var/log/p0f2reputation.out.csv','w')

    # Main loop
    #logs = {}
    asInfo = {}
    dnsInfo = {}
    # Logging file
    #logging.basicConfig(level=logging.INFO,filename='botclientsyslog.py.log')
    #logging.info('SYSLOG log file analysis started')

    lineCounter=-1            
    
    while True:
        lineCounter=lineCounter+1
###############################
#    if lineCounter >= 3000:
#        sys.exit(0)
###############################        
        line1 = fpIn.readline()
        if not line1: break
        if line1[0] == '#':			# ignore leading # comment 
            #print "Ignore # comment"
            continue
        if line1.find("distance") == -1:	# all valid lines have 'distance' in them"
            continue
        print "----------------------------------------------"
        
        fields = line1.split(' ')
        print fields
        numb = len(fields)
        print "numb fields is " + `numb`
        
        os         = fields[8]
        # re-write this using regular expressions and make a function so that it can be reused
        # !!!!!!!!!!!!!!!!!!!!!!!        
        if line1.find("Linux") !=-1:
            if numb == 17:            
                ipStr,port = fields[12].split(':')	# dest IP and dest TCP port number    
            elif numb == 24:
                ipStr,port = fields[17].split(':')	# dest IP and dest TCP port number
        elif line1.find("Windows") != -1 :
            if numb == 19:
                ipStr,port = fields[14].split(':')		# dest IP and dest TCP port number
        elif line1.find("Novell") != -1 :    
            continue						# ignore Novell for moment
            #if numb == 19:
            #    ipStr,port = fields[13].split(':')		# dest IP and dest TCP port number
        else:
            sys.exit("Failed to parse")
          
        
        print "line=" + `lineCounter` + ": *** haxx0r : ip=" + ipStr + " port=" + port + " os=" + os
        
        dnsInfo    = ipintellib.ip2name(ipStr)	        # resolve get DNS name	
        asInfo     = ipintellib.ip2asn(ipStr)        	# get AS information from WHOIS whob
        reputation = ipintellib.ip2reputation(ipStr)	# does slow things down...
        geoIP      = ipintellib.geo_ip(ipStr)
                
        result = ipStr + "," + dnsInfo['name'].strip('.') + \
                         "," + asInfo['as'] + ",ASowner=" + asInfo['registeredCode'] + ",ASnetblock=" + asInfo['netblock'] + ",ASregistry=" + asInfo['registry'] + \
                         ",geoIPcountry=" + geoIP['countryCode'] + ",geoIPcity=" + geoIP['city'] + ",geoIPlat=" + "%.2f" % geoIP['latitude'] + ",geoIPlong=" + "%.2f" % geoIP['longitude'] + \
                         ",zen.spamhaus="           + reputation['zen.spamhaus.org'] + \
                         ",dnsbl.ahbl.org="         + reputation['dnsbl.ahbl.org'] + \
                         ",bl.deadbeef.com="        + reputation['bl.deadbeef.com'] + \
                         ",bogons.cymru.com="       + reputation['bogons.cymru.com'] + \
                         ",zombie.dnsbl.sorbs.net=" + reputation['zombie.dnsbl.sorbs.net'] + \
                         ",bl.spamcop.net="         + reputation['bl.spamcop.net'] + \
                         ",dul.dnsbl.sorbs.net="    + reputation['dul.dnsbl.sorbs.net'] + \
                         ",l2.apews.org="           + reputation['l2.apews.org'] + \
                         ",virus.rbl.msrbl.net="    + reputation['virus.rbl.msrbl.net'] + \
                         ",phishing.rbl.msrbl.net=" + reputation['phishing.rbl.msrbl.net'] + \
                         ",images.rbl.msrbl.net="   + reputation['images.rbl.msrbl.net'] + \
                         ",spam.rbl.msrbl.net="     + reputation['spam.rbl.msrbl.net']  

        
        print result        
        print >> fpOut0,ipStr + "," + "os" + reputation['zen.spamhaus.org']
     

########
# MAIN #
########
if __name__ == '__main__': test()
