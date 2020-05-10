#!/usr/local/bin/python

# This is a copy of ipintellib with unecessary functions removed

# OS dependencies :-
# 1. 'whois' command is installed ; needed for BGP AS information
# 2. 'host' command  is installed ; needed for DNS lookup information

# standard Python
import os, re
import sys, syslog

# 3rd party python libraries
import IPy		# get from Internet, requires 'setuptools' python utility to have been installed 

# Faking -----------------------------------------------------------------------------------------
# note : AS (via whois) info and DNS info do not need external libraries
#Fake = True	# set to true to fake Maxmind GeoIP. AS and DNS info does not need external libraries
Fake = False	# normal operation, if Maxmind GeoIP C API, database and Python bindings have been installed

RichardIP = "217.41.27.169"
MatIP     = "12.12.12.12"

if Fake == False:
# 3rd party Python
    import GeoIP
# ------------------------------------------------------------------------------------------------

Version = "1.0"
Geo_ip_dbase = "/usr/local/share/GeoIP/GeoIPCity.dat"

# Get a file handle for the GeoIP database     
if Fake == False :         
    try:
        #print "Opening GeoIP City database..."
        Gi = GeoIP.open(Geo_ip_dbase,GeoIP.GEOIP_STANDARD)
    except Exception,e:
        print "Exception" + `e` 
        syslog.syslog("blackrain_ipintellib.py() : Exception " + `e` + " caught whilst opening GeoIP City database " + Geo_ip_dbase)
        sys.exit(-1)
    
# Get version of this library  
def getVersion():
    global Version
    return Version
    
# Get the database file location
def getDatabase():
    global Geo_ip_dbase
    return Geo_ip_dbase

# THE MASTER FUNCTION is stored on node mars !!!!
# Return a return list with Country_Code and City for the supplied IP address 
def geo_ip(ip):
    global Gi
    resultDict = {}
    resultDict['result'] = True
    
    # richard's IP
    if Fake == True and ip == RichardIP :
        resultDict['countryName']  = 'F_GB'		# F_* indicates 'faked'
        resultDict['countryCode']  = 'F_United Kingdom' # F_* indicates 'faked'
        resultDict['city']         = 'F_Newbury' 	# F_* indicates 'faked'
        resultDict['region']       = 'None'
        resultDict['dmaCode']      = 'None'		
        resultDict['areaCode']     = 'None'		
        resultDict['latitude']     = 52.0	# made up
        resultDict['longitude']    = 0.00	# made up
        resultDict['postCode']     = 'None'		
        return resultDict

    # mat's IP
    if Fake == True and ip == MatIP :
        resultDict['countryName']  = 'F_GB'		# F_* indicates 'faked'
        resultDict['countryCode']  = 'F_United Kingdom'	# F_* indicates 'faked'
        resultDict['city']         = 'F_Reading'	# F_* indicates 'faked'	
        resultDict['region']       = 'None'
        resultDict['dmaCode']      = 'None'		
        resultDict['areaCode']     = 'None'		
        resultDict['latitude']     = 53.0	# made up
        resultDict['longitude']    = 1.00	# made up
        resultDict['postCode']     = 'None'		
        return resultDict

    #print "geo_ip(" + ip + ")"
    try:
        if not isPublicIP(ip):	   			# this is an RFC 1918 address 
            resultDict['countryName']  = 'None'
            resultDict['countryCode']  = 'None'
            resultDict['city']         = 'None' 	
            resultDict['region']       = 'None'
            resultDict['dmaCode']      = 'None'		# US and Canada
            resultDict['areaCode']     = 'None'		# US and Canada
            resultDict['latitude']     = 999
            resultDict['longitude']    = 999
            resultDict['postCode']     = 'None'		# US and Canada ?

        else:            
            gir = Gi.record_by_addr(ip)
            if gir != None:
            
                #print "gir is " + `gir`
                resultDict['countryName']  = gir['country_name']
                
                resultDict['countryCode']  = gir['country_code']
                if resultDict['countryCode']  == None:
                    resultDict['countryCode'] = 'None'
                
                resultDict['city']         = gir['city']
               	if resultDict['city'] == None:
               	    resultDict['city'] = 'None'
                
                resultDict['region']       = gir['region']
                resultDict['dmaCode']      = gir['dma_code']		# US and Canada
                resultDict['areaCode']     = gir['area_code']		# US and Canada
                resultDict['latitude']     = gir['latitude']
                resultDict['longitude']    = gir['longitude']
                resultDict['postCode']     = gir['postal_code']		# US and Canada only ?
                if resultDict['postCode'] == None:
                    resultDict['postCode'] = 'None'
            else:							# geo_ip has no information
                resultDict['countryName']  = gir['geoip-failed']
                resultDict['countryCode']  = gir['geoip-failed']
                resultDict['city']         = gir['geoip-failed'] 	
                resultDict['region']       = gir['geoip-failed']
                resultDict['dmaCode']      = gir['geoip-failed']
                resultDict['areaCode']     = gir['geoip-failed']		
                resultDict['latitude']     = gir['geoip-failed']
                resultDict['longitude']    = gir['geoip-failed']
                resultDict['postCode']     = gir['geoip-failed']		
            
        #print resultDict         
        return resultDict     
    
    except Exception,e:
        #print "Caught exception " + `e` + " in geo_ip():ip=" + ip
        resultDict['result']       = False
        resultDict['countryName']  = '?'
        resultDict['countryCode']  = '?'
        resultDict['city']         = '?' 	
        resultDict['region']       = '?'
        resultDict['dmaCode']      =  0
        resultDict['areaCode']     =  0		
        resultDict['latitude']     =  0
        resultDict['longitude']    =  0
        resultDict['postCode']     = '?'
        syslog.syslog("Caught exception " + `e` + " in geo_ip(): ip=" + ip)
        return resultDict
    
    #print resultDict         
    #return resultDict     
          
###################################    
# Query Team Cymru server to determine Whois information 
# return : asNumber ipaddress netBlock registry countryCode registered
# On one PC, I get a warning return from Cymru - this code has been tested
# against that scenario only
# IP with no Registered Name = 62.209.152.246 - good for testing


def ip2asn(ip):
    resultDict = {}
    global GlobalAS

# Classic case is 0.0.0.0
    if not isPublicIP(ip):
        #print "ip2asn():  Could not determine AS for non-public IP address : ",ip
        resultDict['as']             = 'AS-none'
        resultDict['netblock']       = 'whois-failed'
        resultDict['countryCode']    = 'whois-failed'
        resultDict['registry']       = 'whois-failed'
        resultDict['registeredCode'] = 'whois-failed'
        resultDict['registeredName'] = 'whois-failed'
        return resultDict

    cmdLine = "whois -h whois.cymru.com -v " + ip
    #print "cmdLine :",cmdLine	

    try:
    	pipe = os.popen(cmdLine,'r')
    	raw = pipe.read()
    	#print "raw=",raw
    	#print "length of raw is " + `len(raw)`
    	raw2 = raw.replace('\n','|');
    	#print "raw2=" + raw2
    			
    	n = raw2.split('|')
        #print "raw2.split()=" + `n`
        
        if len(n) <= 2:
            syslog.syslog("ip2asn(): not enough fields returned by WHOIS for ",ip)
            resultDict['as']             = 'AS-none'
            resultDict['netblock']       = 'whois-failed'
            resultDict['countryCode']    = 'whois-failed'
            resultDict['registry']       = 'whois-failed'
            resultDict['registeredCode'] = 'whois-failed'  
            resultDict['registeredName'] = 'whois-failed' 
            return resultDict   
        
        if "Warning" in n[0] :
            resultDict['as']   = "AS" + n[8].strip()
            #print resultDict['as']
            
            if "ASNA" in resultDict['as'] :	
                print "ip2asn(): WHOIS server could not determine AS for IP address : ",ip
                resultDict['as']             = 'AS-none'
                resultDict['netblock']       = 'whois-failed'
                resultDict['countryCode']    = 'whois-failed'
		resultDict['registry']       = 'whois-failed'
                resultDict['registeredCode'] = 'whois-failed'  
                resultDict['registeredName'] = 'whois-failed'  # e.g. VODAFONE ITALY
            else:	# OK
                resultDict['netblock']       = n[10].strip()
                resultDict['countryCode']    = n[11].strip()
                resultDict['registry']       = (n[12].strip()).upper()	# Register e.g. RIPE,ARIN seems to be in lower-case ?

	        # Split Register information into two parts
	        # This can be blank !
                if len(n[14]) <= 2:
                    resultDict['registeredName'] = "**None**"
                    resultDict['registeredCode'] = "**None**"
                else:    
                    registered  = n[14].strip()		          # Lose leading and trailing whitespace
                    r           = registered.split()	      
                    resultDict['registeredCode']  = r[0]	  # Pull out the first entry e.g. VODAFONE_UK
                    r.pop(0)				          # Delete the first entry
                    resultDict['registeredName']  = ' '.join(r)   # Join up the remainder of the entries
                 
                # Prettify the known Vodafone Group AS names
                if resultDict['as'] == 'AS15502' : resultDict['registeredCode'] = "VF-IE"
                if resultDict['as'] == 'AS12663' : resultDict['registeredCode'] = "VF-GRP-SEDC"
                if resultDict['as'] == 'AS30722' : resultDict['registeredCode'] = "VF-IT"
                if resultDict['as'] == 'AS13083' : resultDict['registeredCode'] = "VF-DE"
                if resultDict['as'] == 'AS15480' : resultDict['registeredCode'] = "VF-NL"
                if resultDict['as'] == 'AS3209'  : resultDict['registeredCode'] = "VF-ARCOR"
                if resultDict['as'] == 'AS34419' : resultDict['registeredCode'] = "VF-GRP-IPBB"
                if resultDict['as'] == 'AS12353' : resultDict['registeredCode'] = "VF-PT"
                if resultDict['as'] == 'AS12430' : resultDict['registeredCode'] = "VF-ES"
                if resultDict['as'] == 'AS21334' : resultDict['registeredCode'] = "VF-HU"
                if resultDict['as'] == 'AS25135' : resultDict['registeredCode'] = "VF-UK"
                
                # Prepend tag for the known big Tier 1 AS
                # Need to add Interroute
                if resultDict['as'] == 'AS3549'  : resultDict['registeredCode'] = "T1:GC"
                if resultDict['as'] == 'AS1239'  : resultDict['registeredCode'] = "T1:SPRINT"
                if resultDict['as'] == 'AS3356'  : resultDict['registeredCode'] = "T1:LEVEL3"
                
                # Prepend tag for the IPBB transit providers - Colt
                if resultDict['as'] == 'AS5400'  : resultDict['registeredCode'] = "TR:BT"
                if resultDict['as'] == 'AS13237' : resultDict['registeredCode'] = "TR:LAMBDANET"
                
                # Prepend tag for the "Competitors"
                if resultDict['as'] == 'AS3125'  : resultDict['registeredCode'] = "COMP:FT-ORANGE"
                
        else:
            print "\nParse failed\n"    
            print "n[0]:" ,n[0]
            print "n[1]:" ,n[1]
            print "n[2]:" ,n[2]
            print "n[3]:" ,n[3]
            print "n[4]:" ,n[4]
            print "n[5]:" ,n[5]
            print "n[6]:" ,n[6]
            print "n[7]:" ,n[7]
            print "n[8]:" ,n[8]
            print "n[9]:" ,n[9]
            print "n[10]:",n[10]
            print "n[11]:",n[11]
            print "n[12]:",n[12]
            print "n[13]:",n[13]
            print "n[14]:",n[14]	

    except Exception,e:
        syslog.syslog("Exception " + `e` + " in ip2asn(): ip=" + ip + " raw2=" + raw2);
	resultDict['as']             = 'AS-none'
        resultDict['netblock']       = 'whois-failed'
        resultDict['countryCode']    = 'whois-failed'
        resultDict['registry']       = 'whois-failed'
        resultDict['registeredCode'] = 'whois-failed'  
        resultDict['registeredName'] = 'whois-failed' 
        return resultDict   
        
    #print resultDict['registeredName'] 
    
    return resultDict

# Look in /etc/hosts for a DNS name and return IP address if found
# else retun None
def name2ipHosts(name): 
    
    try:
        fpIn = open("/etc/hosts","r")
        
        for line in fpIn.readlines():
            if line.find(name) != -1:
                #print "found it : " + line
                pat = "\d+.\d+.\d+.\d+"
                ips = re.findall(pat,line)
                #print ips
                #print ips[0]
                return ips[0]
        return None 
    except Exception,e:
        syslog.syslog("Exception " + `e` + " in name2ipHosts(): name=" + name);
        return None
    
    #	pipe = os.popen(cmdLine,'r')
    #	raw = pipe.read()
    #	raw = raw.replace('\n',' ');	# Replace trailing \n
    #    #print "ip2name(): raw:" ,raw	
#
#        if raw.find("not found") != -1: 
#            # print "****not found"
#            raw = raw.split()
 #           dns['status'] = raw[4]
 #           dns['name']   = "NoDNS"
#        elif raw.find("connection timed out") != -1:


# Convert IP address to DNS name
# Convert DNS name to IP address
def ip2name(ip): 
    dns = {}

    cmdLine = "host " + ip
    # print "ip2name(): cmdLine :",cmdLine	

    try:
    	pipe = os.popen(cmdLine,'r')
    	raw = pipe.read()
    	raw = raw.replace('\n',' ');	# Replace trailing \n
        #print "ip2name(): raw:" ,raw	

        if raw.find("not found") != -1: 
            # print "****not found"
            raw = raw.split()
            dns['status'] = raw[4]
            dns['name']   = "NoDNS"
        elif raw.find("connection timed out") != -1:
            dns['status'] = "Timeout"
            dns['name']   = "NoDNS-timeout"
        elif raw.find("localhost") != -1:
            dns['status'] = "OK"
            dns['name']   = "NoDNS"    
        # DNS name to IP mapping
        elif raw.find("is an alias for") != -1:
            pat="\d+.\d+.\d+.\d+"
            ips = re.findall(pat,raw)
            dns['status'] = "Alias"
            dns['name']   = ips[0]    
        elif raw.find("has address") != -1:
            raw = raw.split();
            # print raw
            dns['status'] = "OK"
            dns['name']   = raw[3]
        else:
            # print "***found"
            raw = raw.split()
            # print raw
            dns['status'] = "OK"
            dns['name']   = raw[4]    
            
        # print dns

    except Exception,e:
        syslog.syslog("Exception " + `e` + " in ip2name(): ip=" + ip + " raw=" + raw);
    	#print "ip2name(): Caught exception for following raw data for IP=" + ip
	#print "command-line:" + cmdLine
	#print "raw:" + raw
        dns['name']   = "Exception"
        dns['status'] = "Err"
        return dns
        
    return dns


# ip2reputation is broken !!!!     
# Return TRUE if IP is a non-RFC 1918
# XXX This does not handle 172.16 correctly
# XXX Does no handle 10/8 either...
# return True or False
# return False if any errors
# There is now a library from Team Cymru to perfomr this
def isPublicIP(ip):
#    x = (ip.startswith('192.168.') or ip.startswith('172.30.') or ip.startswith('172.31.') or ip.startswith('10.') or ip.startswith('0.0.0.0'))
#    return not x 


     #rep = ip2reputation(ip)
     #if rep['status'] == True:
     #    if rep['bogons.cymru.com'] == 'OK':
     #        return True
     #    else:
     #        return False
     #else:
     #    return False
     
     if ip.find("0.0.0.0") != -1 :
         return False
     if ip.find("127.0.0.1") != -1 :
         return False
     if ip.find("192.168.1.") != -1 :
         return False
     if ip.find("172.30.") != -1 :
         return False
     if ip.find("172.31.") != -1 :
         return False
    
     return True

#
def hex2dec(s):
#
    """return the integer value of a hexadecimal string s"""
#
    return int(s, 16)

def int2bin(n,count=6) :
    return "".join([str((n >> y) & 1) for y in range(count-1,-1,-1)])
    
##########################################
# Main starts here
##########################################

def test():
    asInfo = {}
    dnsInfo = {}
    
    print "\n\n\n\n"
    print "==============================================="
    print "BlackRain : IP Intelligence Library Test Module"
    print "==============================================="
    print "Library version           : " + getVersion()
    print "GeoIP dbase file location : " + getDatabase()
    print "Fake GeoIP info           : " + `Fake`

    print "\n----------------"
    print "Hard-coded tests"
    print "----------------\n"

    
    # IP to DNS name
    ipStr = "0.0.0.0"				# corner case
    dnsInfo  = ip2name(ipStr)	        	# resolve get DNS name	
    print ipStr + " resolves to " + dnsInfo['name']

    # DNS name to IP using /etc/hosts
    name  = "rocknroll.dyndns.org"	# 
    ip = name2ipHosts(name)	       	# resolve get DNS name	
    print name + " resolves via /etc/hosts to " + ip.__str__()
    
    # DNS name to IP using /etc/hosts
    name  = "www.google.com"		# 
    ip = name2ipHosts(name)	       	# resolve get DNS name	
    print name + " resolves via /etc/hosts to " + ip.__str__()

    # IP to DNS name
    ipStr = "127.0.0.1"				# corner case 
    dnsInfo  = ip2name(ipStr)	        	# resolve get DNS name	
    print ipStr + " resolves to " + dnsInfo['name']

    # IP to DNS name
    ipStr = "255.255.255.255"			# corner case 
    dnsInfo  = ip2name(ipStr)	        	# resolve get DNS name	
    print ipStr + " resolves to " + dnsInfo['name']

    # IP to DNS name
    ipStr = "270.255.255.255"			# nonsense IP 
    dnsInfo  = ip2name(ipStr)	        	# resolve get DNS name	
    print ipStr + " resolves to " + dnsInfo['name']

    # IP to DNS name
    ipStr = "217.41.27.169"			# My home ADSL IP
    dnsInfo  = ip2name(ipStr)	        	# resolve get DNS name	
    print ipStr + " resolves to " + dnsInfo['name']

    # DNS name to IP
    ipStr = "www.openbsd.org"
    dnsInfo  = ip2name(ipStr)	        	# resolve get DNS name	
    print ipStr + " resolves to " + dnsInfo['name']
    
    # DNS name to IP
    ipStr = "www.google.com"
    dnsInfo  = ip2name(ipStr)	        	# resolve get DNS name	
    print ipStr + " resolves to " + dnsInfo['name']
    
    # Richard's IP 
    ipStr      = RichardIP
    dnsInfo    = ip2name(ipStr)		
    asInfo     = ip2asn(ipStr)  
    geoIP      = geo_ip(ipStr)
                
    result = ipStr + "," + dnsInfo['name'].strip('.') + \
                     "," + asInfo['as'] + ",registeredCode=" + asInfo['registeredCode'] + ",registeredName=" + asInfo['registeredName'] + ",ASnetblock=" + asInfo['netblock'] + ",ASregistry=" + asInfo['registry'] + \
                     ",geoIPcountryName=" + geoIP['countryName'] + ",geoIPcountry=" + geoIP['countryCode'] + ",geoIPcity=" + geoIP['city'] + ",geoIPlat=" + "%.2f" % geoIP['latitude'] + ",geoIPlong=" + "%.2f" % geoIP['longitude']
    print "\nRichard's IP :\n" + result
    
    # Mat's IP 
    ipStr      = MatIP
    dnsInfo    = ip2name(ipStr)		
    asInfo     = ip2asn(ipStr)  
    geoIP      = geo_ip(ipStr)
                
    result = ipStr + "," + dnsInfo['name'].strip('.') + \
                     "," + asInfo['as'] + ",registeredCode=" + asInfo['registeredCode'] + ",registeredName=" + asInfo['registeredName'] + ",ASnetblock=" + asInfo['netblock'] + ",ASregistry=" + asInfo['registry'] + \
                     ",geoIPcountryName=" + geoIP['countryName'] + ",geoIPcountry=" + geoIP['countryCode'] + ",geoIPcity=" + geoIP['city'] + ",geoIPlat=" + "%.2f" % geoIP['latitude'] + ",geoIPlong=" + "%.2f" % geoIP['longitude']
    print "\nMat's IP :\n" + result
  
      
    print "\n-------------------------"
    print "Test data taken from file"
    print "-------------------------\n"
    
    # input file : file of IPs (hand-crafted)
    fpIn   = open(r'blackrain_ipintellib.test.in.csv','r')

    # output file 
    #fpOut0 = open(r'blackrain_ipintellib.test.out.csv','w')

    # Logging file
    #logging.basicConfig(level=logging.INFO,filename='botclientsyslog.py.log')
    #logging.info('SYSLOG log file analysis started')

    lineCounter = -1            
    
    while True:
        lineCounter=lineCounter+1
###############################
#    if lineCounter >= 3000:
#        sys.exit(0)
###############################        
        line1 = fpIn.readline()
        if not line1: break
        if line1[0] == '#':			# ignore leading # comment 
            continue
        
        fields = line1.split(',')
        print "----------------------------------------------"
    
        ipStr = fields[0].strip()
        print "IP=" + ipStr    
        
        dnsInfo    = ip2name(ipStr)	        # resolve get DNS name	
        asInfo     = ip2asn(ipStr)        	# get AS information from WHOIS whob
        #reputation = ip2reputation(ipStr)	# does slow things down...
        geoIP      = geo_ip(ipStr)
                
        result = ipStr + "," + dnsInfo['name'].strip('.') + \
                         "," + asInfo['as'] + ",ASowner=" + asInfo['registeredCode'] + ",ASnetblock=" + asInfo['netblock'] + ",ASregistry=" + asInfo['registry'] + \
                         ",geoIPcountry=" + geoIP['countryCode'] + ",geoIPcity=" + geoIP['city'] + ",geoIPlat=" + "%.2f" % geoIP['latitude'] + ",geoIPlong=" + "%.2f" % geoIP['longitude']
  
        print result        
                      
        #print >> fpOut0,result
     

########
# MAIN #
########
if __name__ == '__main__': test()
