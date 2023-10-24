#!/usr/bin/python

# This is the definitive function as a library

import GeoIP
import os
import sys,syslog,time
import re
import IPy
import pkg_resources

Version = "1.10"

GlobalAS = {}			# List of most popular AS - do not delete
#Geo_ip_dbase = "/usr/local/share/GeoIP/GeoIPCity.dat"
Geo_ip_dbase = "/usr/local/share/GeoIP/GeoLiteCity.dat"
    
# Get a file handle for the GeoIP database     
try:
    #print "Opening GeoIP City database..."
    Gi=GeoIP.open(Geo_ip_dbase,GeoIP.GEOIP_STANDARD)
except Exception,e:
    print "Exception" + `e` 
    syslog.syslog("ipintellib.py() : Exception " + `e` + " caught whilst opening GeoIP City database " + Geo_ip_dbase)
    sys.exit(-1)
    
# Get version of the library  
def getVersion():
    global Version
    return Version
    
# Get the database location
def getDatabase():
    global Geo_ip_dbase
    return Geo_ip_dbase

# THIS IS THE MASTER FUNCTION on mars !!!!
# Return a return list with Country_Code and City for the supplied IP address 
def geo_ip(ip):
    global Gi
    resultDict = {}
    resultDict['result'] = True
    
    #print "Entered geo_ip(" + ip + ")"
    try :
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
            return resultDict
            
        else :            
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
        
        # I think the GeoIP API is possibly a bit crap and just throws an exception if the IP can't be found, so don't log this
        #print "Caught exception " + `e` + " in geo_ip(): ip=" + ip
        #syslog.syslog("Caught exception " + `e` + " in geo_ip(): ip=" + ip)
        return resultDict
    
    #print resultDict         
    #return resultDict     

# add try: handling
# separator by default is ' ' , i.e. a space
def prettyAS(ip,separator=None):
    asMsg = ""
    
    if separator == None:
        sep = " "
    else:
        sep = ","    
    
    if ip != None:
        # print "prettyAS() : IP found = " + ip
        # WHOIS information
        asInfo = ip2asn(ip)
        asNum =  asInfo['as']                                   # AS123 
        asRegisteredCode = asInfo['registeredCode']             # Short-form e.g. ARCOR
        asRegistry = asInfo['registry']				# e.g. ARIN
        asNetblock = asInfo['netblock']				# e.g. 123.232.2.0/24
        #asMsg = asRegisteredCode + " (" + asNum + ") " + asRegistry + " [" + asNetblock + "]" 
        #asMsg = asRegisteredCode + sep + "(" + asNum + ")" + sep + asRegistry + sep + "[" + asNetblock + "]" 
        
        #asMsg = asRegisteredCode + sep + asNum + sep + asRegistry + sep + asNetblock 
        # Join AS number and RIR with '-' so that they do not get searched by Twitter
        asMsg = asRegisteredCode + sep + asNum + '-' + asRegistry + sep + asNetblock 
                                                        
    #print "AS info : " + asMsg     
    return asMsg


WhoisCache = {}

def ip2asn(ip):
    resultDict = {}
    global WhoisCache

    try: 
        
        # defensive code to sanitise this functions ip parameter in case an application is calling with duff ip parameter
        pat = '\d+\.\d+\.\d+\.\d+'
        a = re.findall(pat,ip)
        if len(a) != 0 :
            ip = a[0]

        if not isPublicIP(ip):
            #print "ip2asn():  Could not determine AS for non-public IP address : ",ip
            resultDict['as']             = 'AS-none'
            resultDict['netblock']       = 'whois-failed'
            resultDict['countryCode']    = 'whois-failed'
            resultDict['registry']       = 'whois-failed'
            resultDict['registeredCode'] = 'whois-failed'
            resultDict['registeredName'] = 'whois-failed'
            return resultDict
 
        # is the IP in the cache already ?
        if WhoisCache.has_key(ip) == True :
            msg = "ipintellib.py : WHOIS_CACHE_HIT: " + ip 
            #print msg
            #syslog.syslog(msg)
            return WhoisCache[ip]
        else :
            msg = "ipintellib.py : WHOIS_CACHE_MISS: " + ip 
            #print msg
            #syslog.syslog(msg)
        
        # IP is not cached so call to Cymru to determine AS info    
        for i in range(3) :	# 3 attempts
            result = ip2asnAtom(ip)
            if result != None :
                msg = "added AS info for " + ip + " to WhoisCache"
                #print msg
                #syslog.syslog(msg)
                WhoisCache[ip] = result
                return result
            msg = "ipintellib.py : WARNING: ip2asn() failed to determine AS info on attempt " + i.__str__() + " for ip " + ip
            #print msg
            syslog.syslog(msg)
            time.sleep(1)
        
        # no good result even after rettry schedule so return a fail
        resultDict['as']             = 'AS-none'
        resultDict['netblock']       = 'whois-failed'
        resultDict['countryCode']    = 'whois-failed'
        resultDict['registry']       = 'whois-failed'
        resultDict['registeredCode'] = 'whois-failed'  
        resultDict['registeredName'] = 'whois-failed' 
        return resultDict
            
    except Exception,e:
        syslog.syslog("Exception " + `e` + " in ip2asn(): ip=" + ip)
	resultDict['as']             = 'AS-none'
        resultDict['netblock']       = 'whois-failed'
        resultDict['countryCode']    = 'whois-failed'
        resultDict['registry']       = 'whois-failed'
        resultDict['registeredCode'] = 'whois-failed'  
        resultDict['registeredName'] = 'whois-failed' 
        return resultDict   
                                                            
                                                                          

###################################    
# Query Team Cymru server to determine Whois information 
# return : asNumber ipaddress netBlock registry countryCode registered
# On one PC, I get a warning return from Cymru - this code has been tested
# against that scenario only
# IP with no Registered Name = 62.209.152.246 - good for testing
#
#root@mars:/home/crouchr#  whois -h whois.cymru.com -v 184.22.55.93
#Warning: RIPE flags used with a traditional server.
#AS      | IP               | BGP Prefix          | CC | Registry | Allocated  | AS Name
#21788   | 184.22.55.93     | 184.22.48.0/20      | US | arin     | 2010-12-22 | NOC - Network Operations Center Inc.
#
#root@mars:/home/crouchr#  whois -h whois.cymru.com -v 8.8.8.8     
#Warning: RIPE flags used with a traditional server.
#AS      | IP               | BGP Prefix          | CC | Registry | Allocated  | AS Name
#15169   | 8.8.8.8          | 8.8.8.0/24          | US | arin     | 1992-12-01 | GOOGLE - Google Inc.

# return None if fatal error that wont be solved by a retry
def ip2asnAtom(ip):
    resultDict = {}
    #global GlobalAS

    cmdLine = "whois -h whois.cymru.com -v " + ip
    #syslog.syslog("ipintellib.py : ip2asnAtom() : " + cmdLine)
    #print "cmdLine :",cmdLine	

    try:
    	pipe = os.popen(cmdLine,'r')
    	raw = pipe.read()
    	#print "raw=",raw
    	#print "length of raw is " + `len(raw)`
        if len(raw) == 0 :
            return None
        if raw.find("Error") != -1 :
           return None
        
    	raw2 = raw.replace("Warning: RIPE flags used with a traditional server.","")
    	raw2 = raw2.replace('\n','|');
    	#print "raw2=" + raw2
    			
    	n = raw2.split('|')
        #print "n=" + `n`
        
        if len(n) <= 2:
            syslog.syslog("ip2asn(): not enough fields returned by WHOIS for ",ip)
            return None
 
        else :
            resultDict['as']             = n[8].strip(" ")
            resultDict['netblock']       = n[10].strip(" ")
            resultDict['countryCode']    = n[11].strip(" ")
            resultDict['registry']       = n[12].strip(" ")
            resultDict['registry']       = resultDict['registry'].upper()
            a = n[14].lstrip(" ")
            resultDict['registeredCode'] = a.split(" ")[0].strip(" ")  
            name = a.split(" ")
            resultDict['registeredName'] = ' '.join(name[1:]).strip(" ") 
            resultDict['registeredName'] = resultDict['registeredName'].lstrip("- ") 
            #print resultDict
            return resultDict   
        
    except Exception,e:
        msg = "Exception " + `e` + " in ip2asnAtom(): ip=" + ip + " raw2=" + raw2
        print msg
        syslog.syslog(msg)
	return None


# Query various Blackhole DNS Services to determine the reputation of the src IP 
# return : DNS_returns codes as a list :
# dnsbl.ahbl.org
# bl.deadbeef.com
# bogons.cymru.com
# zombie.dnsbl.sorbs.net
# tor.ahbl.org
# zen.spamhaus.org
#
# On one PC, I get a warning return from Cymru - this code has been tested
# against that scenario only
# This required arblcheck 1.6 to run 
# This is now the MASTER on mail
def ip2reputation(ip): 
    reputation = {}

    cmdLine = "/usr/local/bin/arblcheck " + ip
    #print "cmdLine :",cmdLine	

    try:
    	pipe = os.popen(cmdLine,'r')
    	raw = pipe.read()
    	raw2 = raw.replace('\n',':');
        #print "raw:\n" ,raw	
    	#print "raw2:\n",raw2		
    	n = raw2.split(':')
        nf = len(n)				# number of fields
        reputation['status'] = True
        reputation[n[2]]  = spamhausToMsg(n[3])
        reputation[n[6]]  = abuseToMsg(n[7])
        reputation[n[10]] = deadbeefToMsg(n[11])
        reputation[n[14]] = cymruToMsg(n[15])
        reputation[n[18]] = hijackedToMsg(n[19])
        
        # remaining RBLs not fully tested yet !!!
        reputation[n[22]]  = rblToMsg(n[23])	# "bl.spamcop.net",
        reputation[n[26]]  = rblToMsg(n[27])	# "dul.dnsbl.sorbs.net",    - Hijacked netblock
        reputation[n[30]]  = rblToMsg(n[31])    # "l2.apews.org",
        reputation[n[34]]  = rblToMsg(n[35])    # "virus.rbl.msrbl.net",   - IP sending email with viruses
        #reputation[n[38]]  = rblToMsg(n[39])	# "phishing.rbl.msrbl.net" - IP sending phishing emails
        #reputation[n[42]]  = rblToMsg(n[43])	# "images.rbl.msrbl.net"   - IP sending spam with images
        #reputation[n[46]]  = rblToMsg(n[47])	#" spam.rbl.msrbl.net",
                
        #print reputation

    except Exception,e:
    	syslog.syslog("Exception " + `e` + " in ip2reputation(): ip=" + ip + " nf=" + `nf` + " raw2=" + raw2);
    	#print "ip2reputation(): Caught exception for following raw data for IP=" + ip
	#print "command-line:" + cmdLine
	#print "raw2:" + raw2
        reputation['status'] = False
        
    return reputation

# return True is any single reputation is not 'OK'
def interestingReputation(reputation):
    
    interesting = False
    
    #print reputation.values()
    for i in reputation.values():
        #print type(i)
        if type(i) == bool:
            continue 
        if i.find("!") != -1 :
            interesting = True
        
    
    #    if i != 'OK' and not i.has_key('status') :
    #        interesting = True
    #        print "Found an interesting IP " + `reputation`    
    return interesting

# simple IP to name lookup
# this could be more detailed in future e.g. lookup MX records ? 
# THIS IS THE MASTER

def ip2name(ip): 
    dns = {}

    cmdLine = "host " + ip
    # print "ip2name(): cmdLine :",cmdLine	

    try:
    	pipe = os.popen(cmdLine,'r')
    	raw = pipe.read()
    	raw = raw.replace('\n',' ');	# Replace trailing \n
#        print "ip2name(): raw:" ,raw	

        if raw.find("not found") != -1: 
            # print "****not found"
            raw = raw.split()
            dns['status'] = raw[4]
            dns['name'] = "NoDNS"
        elif raw.find("connection timed out") != -1:
            dns['status'] = "Timeout"
            dns['name'] = "NoDNS-timeout"    
        elif raw.find("is an alias for") != -1:
            raw = raw.split();
            # print raw
            dns['status'] = "Alias"
            dns['name'] = raw[9]
        # DNS name to IP mapping    
        elif raw.find("has address") != -1:
            raw = raw.split();
            # print raw
            dns['status'] = "OK"
            dns['name'] = raw[3]
        else:
            # print "***found"
            raw = raw.split()
            # print raw
            dns['status'] = "OK"
            dns['name'] = raw[4]    
            
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

# Return TCP port name else return the number
def tcpToName(port):
    portList = {
        '21' : 'ftp',
        '22' : 'ssh',
        '23' : 'telnet',
        '25' : 'smtp',
        '80' : 'http',
        '135': 'NetBIOS?'
    }

    if portList.has_key(port):
        return portList[port]
    else:
        return port

# Convert Abuse return code to info message
def abuseToMsg(code):
    codeList = {
        '127.0.0.2'       : 'Open_Relay!',
        '127.0.0.3'       : 'Open_Proxy!',
        '127.0.0.4'       : 'Spam_Source!',
        '127.0.0.5'       : 'Provisional_Spam_Source_Listing!',
        '127.0.0.6'       : 'Form-mail_Spam!',
        '127.0.0.7'       : 'Spam_Supporter!',
        '127.0.0.8'       : 'Spam_Supporter_(indirect)!',
        '127.0.0.9'       : 'End_User_(non_mail_system)!',
        '127.0.0.10'      : 'Shoot_On_Sight!',
        '127.0.0.11'      : 'Non-RFC_Compliant_(postmaster_or_abuse)!',
        '127.0.0.12'      : 'Does_not_properly_handle_5xx_errors!',
        '127.0.0.13'      : 'Other_Non-RFC_Compliant!',
        '127.0.0.14'      : 'Compromised_System_DDoS!',
        '127.0.0.15'      : 'Compromised_System_Relay!',
        '127.0.0.16'      : 'Compromised_System_Autorooter/Scanner!',
        '127.0.0.17'      : 'Compromised_System_Worm_or_mass_mailing_virus!',
        '127.0.0.18'      : 'Compromised_System_Other_virus!',
        '127.0.0.19'      : 'Open_Proxy!',
        '127.0.0.20'      : 'Blog/Wiki/Comment_Spammer!',
        '127.0.0.127'     : 'Other!',
        '255.255.255.255' : 'OK'
    }

    if codeList.has_key(code):
        return codeList[code]
    else:
        return code

# SPAMHAUS
# --------
# Blacklist DNS Servers or RBL Servers
# Convert Spamhaus return code to info message
# XBL = realtime database of IP addresses of hijacked PCs infected by illegal 3rd party exploits
# e.g. open proxies (HTTP,socks,AnalogX,wingate), worms/viruses with built-in spam engines and other
# trojan horse exploits
# SBL = Spamhaus-maintained
# PBL = IP ranges that should not be delivering unauthenticated SMTP email
def spamhausToMsg(code):
    codeList = {
        '127.0.0.2'       : 'SBL!',
        '127.0.0.4'       : 'XBL-CBL!',
        '127.0.0.5'       : 'XBL-NJABL!',
        '127.0.0.10'      : 'PBL-ISP!',
        '127.0.0.11'      : 'PBL-Spamhaus!',
        '255.255.255.255' : 'OK'
    }

    if codeList.has_key(code):
        return codeList[code]
    else:
        return code


# Convert Team Cymru return code to info message
def cymruToMsg(code):
    codeList = {
        '127.0.0.2'       : 'Bogon!',
        '255.255.255.255' : 'OK'
    }

    if codeList.has_key(code):
        return codeList[code]
    else:
        return code

# Convert Deadbeef return code to info message
def deadbeefToMsg(code):
    codeList = {
        '127.0.0.2'       : 'No_abuse@xxx_e-mail_address!',
        '255.255.255.255' : 'OK'
    }

    if codeList.has_key(code):
        return codeList[code]
    else:
        return code

# Convert Hijacked return code to info message
def hijackedToMsg(code):
    codeList = {
        '127.0.0.2'       : 'Netblock_Hijacked!',
        '255.255.255.255' : 'OK'
    }

    if codeList.has_key(code):
        return codeList[code]
    else:
        return code

# Convert Tor return code to info message
def torToMsg(code):
    codeList = {
        '127.0.0.2'       : 'Part_of_TOR_network!',
        '255.255.255.255' : 'OK'
    }

    if codeList.has_key(code):
        return codeList[code]
    else:
        return code

# Generic RBL to info message
def rblToMsg(code):
    codeList = {
        '127.0.0.2'       : 'Bad_Reputation!',
        '255.255.255.255' : 'OK'
    }

    if codeList.has_key(code):
        return codeList[code]
    else:
        return code

# Return TRUE if the AS Code includes VFONE
def isVfoneAs(asCode):
    if asCode.find('VFONE') != -1:
        return True
    else:
        return False    


# return /24 of given IP
# ip = 1.2.3.4
# return 1.2.3.0/24
def getSlash24(ip):
    try:
        a = ip.split(".")
        b = a[0] + "." + a[1] + "." + a[2] + ".0/24"
        return b
    except Exception,e:
        syslog.syslog("ipintellib.py : Exception in getSlash24() " + e.__str__() + " ip=" + ip.__str__()) 
        return "0.0.0.0/24"

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

# where are bytes ???
# write file for tos <> 0
# write netflow.csv for basic parse
# highlight vodafone AS ?
#
# anomaly
# -------
# protocol <> tcp,icmp,udp
# flags = 0
# odd icmp types codes
# is stuff towards ON link addresses ? (whether dropped or not)
# is stuff towards C&C IP addresses ?
# is stuff towards a server for which thee is an MX record -> if not it is spam ?
# decode the TCP flags
# need to reduce size of the source an target
# put City against source IP address ?
# employ some caching so not hammering WHOIS
# some sort of offline mode - i.e. lose the whois info
# make traffic "more interesting [+++] if it is in a Vodafone address range
# maybe give a flow an interesting_index
# make traffic more interesting if it originates from Vodafone AS 
# deaggregation : traffic is interesting if the source mask is /25 , /26, /27, /28, /29 ,/30 , /31 , /32
# mod ip2asn to add "VFONE" to AS if it is a known VF ASN - this can then be picked up in Afterglow using a regex
# use the ip2reputation()
# look for traffic to dark IP space 85.205..
# signature : Use red for real threat else use orange (it is interesting traffic) 
# source : Use different colors for reputation scoring
# source use different shapes for if Vodafone or not 
# destination use different shapes if vodafone or not
# destination : colour = ?
# long lived flows = vpn or covert channel
# AS 15502 Vodafone Ireland
# AS 12663 Vodafone Italy
# AS 13083 Vodafone D2 (Mannesman)
# AS 15480 Vodafone Netherlands
# AS 3209  Arcor
# do another graph with source AS instead of source IP
# do another graph with source IP (bogons etc)
# do another graph with destination = dark IP
# do another graph with dest ip = One Network link and loopback IPs
# Other AS
# AS 25570 MessageLabs DE
# AS 21345 MessageLabs
# initialisation

def main():
    print "\n\n\n\n"
    print "================================="
    print "IP Reputation Library Test Module"
    print "================================="
    print "Library version : " + getVersion()

    srcAs        = {}
    bgpNextHopAs = {}
    dstAs        = {}

    print "Hard-coded tests"
    print "----------------"
    
    # getSlash24
    ipStr = "217.41.27.169"	
    a = getSlash24(ipStr)	     	
    print ipStr + " is in /24 : " + a

    ipStr = "fred"		# failure case	
    a = getSlash24(ipStr)	     	
    print ipStr + " is in /24 : " + a

    # IP to DNS name
    ipStr = "217.41.27.169"			# My IP
    dnsInfo  = ip2name(ipStr)	        	# resolve get DNS name	
    print ipStr + " resolves to " + dnsInfo['name']

    # DNS name to IP
    ipStr = "www.openbsd.org"
    dnsInfo  = ip2name(ipStr)	        	# resolve get DNS name	
    print ipStr + " resolves to " + dnsInfo['name']
    filename = pkg_resources.resource_filename(__name__, "ipintellib.test.in.csv")
    
    # input file : file of IPs (hand-crafted)
    fpIn   = open(filename,'r')

    # output file 
    fpOut0 = open(r'ipintellib.test.out.csv','w')

    # Main loop
    #logs = {}
    asInfo = {}
    dnsInfo = {}
    # Logging file
    #logging.basicConfig(level=logging.INFO,filename='botclientsyslog.py.log')
    #logging.info('SYSLOG log file analysis started')

    lineCounter=-1            
    
    print "Test data taken from file"
    print "-------------------------"
    
    while True:
        try:
            lineCounter=lineCounter+1
###############################
#        if lineCounter >= 3000:
#            sys.exit(0)
###############################        
            line1 = fpIn.readline()
            if not line1: break
            if line1[0] == '#':			# ignore leading # comment 
                #print "Ignore # comment"
                continue
        
            fields = line1.split(',')
            print "----------------------------------------------"
    
            ipStr = fields[0].strip()
            print "ipStr is [" + ipStr + "]"    
        
            dnsInfo    = ip2name(ipStr)	        # resolve get DNS name	
            asInfo     = ip2asn(ipStr)        	# get AS information from WHOIS whob
            reputation = ip2reputation(ipStr)	# does slow things down...
            geoIP      = geo_ip(ipStr)
                
            result = ipStr + "," + dnsInfo['name'].strip('.') + \
                         "," + asInfo['as'] + ",ASowner=" + asInfo['registeredCode'] + ",ASname=" + asInfo['registeredName'] + ",ASnetblock=" + asInfo['netblock'] + ",ASregistry=" + asInfo['registry'] + \
                         ",geoIPcountry=" + geoIP['countryCode'] + ",geoIPcity=" + geoIP['city'] + ",geoIPlat=" + "%.2f" % geoIP['latitude'] + ",geoIPlong=" + "%.2f" % geoIP['longitude']
                         #",zen.spamhaus="           + reputation['zen.spamhaus.org'] + \
                         #",dnsbl.ahbl.org="         + reputation['dnsbl.ahbl.org'] + \
                         #",bl.deadbeef.com="        + reputation['bl.deadbeef.com'] + \
                         #",bogons.cymru.com="       + reputation['bogons.cymru.com'] + \
                         #",zombie.dnsbl.sorbs.net=" + reputation['zombie.dnsbl.sorbs.net'] + \
                         #",bl.spamcop.net="         + reputation['bl.spamcop.net'] + \
                         #",dul.dnsbl.sorbs.net="    + reputation['dul.dnsbl.sorbs.net'] + \
                         #",l2.apews.org="           + reputation['l2.apews.org'] + \
                         #",virus.rbl.msrbl.net="    + reputation['virus.rbl.msrbl.net'] + \
                         #",phishing.rbl.msrbl.net=" + reputation['phishing.rbl.msrbl.net'] + \
                         #",images.rbl.msrbl.net="   + reputation['images.rbl.msrbl.net'] + \
                         #",spam.rbl.msrbl.net="     + reputation['spam.rbl.msrbl.net']  

            print result        
        
            #if interestingReputation(reputation):
            #    print reputation
                
            print >> fpOut0,result
        
        except Exception,e :
            print "Exception : " + e.__str__()     

########
# MAIN #
########
if __name__ == '__main__': 
    main()
