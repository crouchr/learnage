#!/usr/bin/python

import os
import sys
import syslog

## stubb - replace this !!!
def isPublicIP(ip):
    return True

###################################
# Query Team Cymru server to determine Whois information
# return : asNumber ipaddress netBlock registry countryCode registered
# On one PC, I get a warning return from Cymru - this code has been tested
# against that scenario only
# IP with no Registered Name = 62.209.152.246 - good for testing

# this is the new master on firefly - where function is used as a library

def ip2asnCymru(ip):
    resultDict = {}
    global GlobalAS
    
    #raw2 = {}
    #raw3 = {}
    #n    = {}

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
            print "ip2asn(): not enough fields returned by WHOIS for ",ip
            resultDict['as']             = 'AS-none'
            resultDict['netblock']       = 'whois-failed'
            resultDict['countryCode']    = 'whois-failed'
            resultDict['registry']       = 'whois-failed'
            resultDict['registeredCode'] = 'whois-failed'
            resultDict['registeredName'] = 'whois-failed'
            return resultDict

        if cmp(n[0],"Warning:") >= 0 :
            resultDict['as'] = "AS" + n[8].strip()

            #resultDict['as'].strip()   # Leading spaces need to be stripped
            if cmp(resultDict['as'],"ASNA") >=0 :
                #print "ip2asn(): WHOIS server could not determine AS for IP address : ",ip
                resultDict['as']             = 'AS-none'
                resultDict['netblock']       = 'whois-failed'
                resultDict['countryCode']    = 'whois-failed'
                resultDict['registry']       = 'whois-failed'
                resultDict['registeredCode'] = 'whois-failed'
                resultDict['registeredName'] = 'whois-failed'  # e.g. VODAFONE ITALY
            else:       # OK
                resultDict['netblock']       = n[10].strip()
                resultDict['countryCode']    = n[11].strip()
                resultDict['registry']       = (n[12].strip()).upper()  # Register e.g. RIPE,ARIN seems to be in lower-case ?

                # Split Register information into two parts
                # This can be blank !
                if len(n[14]) <= 2:
                    resultDict['registeredName'] = "**None**"
                    resultDict['registeredCode'] = "**None**"
                else:
                    registered  = n[14].strip()                   # Lose leading and trailing whitespace
                    r           = registered.split()
                    resultDict['registeredCode']  = r[0]          # Pull out the first entry e.g. VODAFONE_UK
                    r.pop(0)                                      # Delete the first entry
                    resultDict['registeredName']  = ' '.join(r)   # Join up the remainder of the entries
                # RegisteredCode is the useful one, it is a single word

                #print resultDict['registeredCode'] + " " + resultDict['registeredName']

                # Prettify the known Vodafone Group AS names - keep to two digits if possible
                if resultDict['as'] == 'AS15502' : resultDict['registeredCode'] = "VF-IE"
                if resultDict['as'] == 'AS12663' : resultDict['registeredCode'] = "VF-SEDC"
                if resultDict['as'] == 'AS30722' : resultDict['registeredCode'] = "VF-IT"
                if resultDict['as'] == 'AS13083' : resultDict['registeredCode'] = "VF-DE"
                if resultDict['as'] == 'AS15480' : resultDict['registeredCode'] = "VF-NL"
                if resultDict['as'] == 'AS3209'  : resultDict['registeredCode'] = "VF-ARC"
                if resultDict['as'] == 'AS34419' : resultDict['registeredCode'] = "VF-GRP"	# VF Group
                if resultDict['as'] == 'AS25135' : resultDict['registeredCode'] = "VF-UK"
                if resultDict['as'] == 'AS12353' : resultDict['registeredCode'] = "VF-PT"
                if resultDict['as'] == 'AS21334' : resultDict['registeredCode'] = "VF-HU"
                if resultDict['as'] == 'AS12430' : resultDict['registeredCode'] = "VF-SP"
                if resultDict['as'] == 'AS48728' : resultDict['registeredCode'] = "VF-QT"	# VF Qatar
                
                # Prepend tag for the known big Tier 1 AS
                if resultDict['as'] == 'AS3549'  : resultDict['registeredCode'] = "T1:GLOBAL-CROSSING"
                if resultDict['as'] == 'AS1239'  : resultDict['registeredCode'] = "T1:SPRINT"
                if resultDict['as'] == 'AS3356'  : resultDict['registeredCode'] = "T1:LEVEL3"
                # Prepend tag for the One Network transit providers - Colt
                if resultDict['as'] == 'AS5400'  : resultDict['registeredCode'] = "TR:BT"
                if resultDict['as'] == 'AS13237' : resultDict['registeredCode'] = "TR:LAMBDANET"

                # Prepend tag for the "Competitors"
                if resultDict['as'] == 'AS3125'  : resultDict['registeredCode'] = "COM:FT-ORANGE"

                # Add AS to list of AS we have seen before
                # This is from when function was used inline
                #a = resultDict['as']
                #if GlobalAS.has_key(a):
                    #print "ip2asn(): " + `a` + " has been seen before, i.e. is cached"
                #    GlobalAS[a]+=1
                #else:
                    #print "AS " + `a` + " not seen before"
                #    GlobalAS[a]=1
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
        print "!!!!! ip2asnCymru(): Caught exception for following raw data for IP=" + ip
        print "command-line:" + cmdLine
        print "raw data    :" + raw2
        print "exception   :" + `e`

    #print resultDict['registeredName']

    return resultDict


def ip2asn(ip,routes=0):
    resultDict = {}
    
    #if prefix.find('/') != -1:
    #    ip,junk = prefix.split('/')
    #else:
    #    ip = prefix
           
    resultDict['error']          = None
    resultDict['as']             = '?'
    resultDict['netblock']       = '?'
    resultDict['countryCode']    = '?'
    resultDict['registry']       = '?'
    resultDict['registeredCode'] = '?'
    resultDict['registeredName'] = '?'
    resultDict['info']           = '?'
    resultDict['abuse']          = '?'
    resultDict['purpose']	 = '?'	# search for keywords in "info"    
    resultDict['vodafone']	 = '?'	# search for Vodafone-related keywords in "info"    
    
    # Classic case is 0.0.0.0
    #if not isPublicIP(ip):
    #    return resultDict

    # -t : display country code as TLD not full name
    # +a : display origin AS (if available)
    if routes == 0:
        cmdLine = "/usr/local/bin/zcw -t -h " + ip
    else:
        cmdLine = "/usr/local/bin/zcw -t -h +a " + ip
    #print "cmdLine :",cmdLine

    try:
        pipe = os.popen(cmdLine,'r')
        raw = pipe.read()
        #print "raw=",raw
        #print "length of raw is " + `len(raw)`
        
        raw2 = raw.split('\n');
        #print "raw2=[" + `raw2` + "]"

        for i in raw2:
            i = i.strip()
            if len(i) < 3: break
            
            #print "i is [" + i + "]"
            #if i.find("route:") != -1:
            #    a,b = i.split(":")
            #    resultDict['netblock'] = b.lstrip(" ")
            if i.find("Country") != -1:
                a,b = i.split(":")
                resultDict['countryCode'] = b.lstrip(" ")
                #print "-> countrycode is " + resultDict['countryCode']
            if i.find("ERROR") != -1 or i.find("error") != -1 :
                resultDict['error'] = i.strip("\n")
                #print "-> error is : " + resultDict['error']
                syslog.syslog("Report to whois-error@cyberwhois.org : zcw returned error " + resultDict['error'] + " for IP " + ip)
                return resultDict    
            #if i.find("city:") != -1:
            #    a,b = i.split(":")
            #    resultDict['city'] = b.lstrip(" ") 
            if i.find("Announced by") != -1:
                a,b = i.split(":")
                #print "a is [" + a + "] b is [" + b +"]"
                b=b.strip(" ")
                #print "b is [" + b + "]"
                
                c=b.split(" ")
                #print "c is [" + `c` + "]"
                resultDict['as']=c[0]
                #print "-> AS is " + resultDict['as']
                
                d=" ".join(c[1:])
                #print "d is [" + d + "]"
                d=d.lstrip('(')
                d=d.rstrip(')')
                resultDict['registeredName'] = d
                #print "-> registeredName is " + resultDict['registeredName']
                
            if i.find("Network name") != -1:
                a,b = i.split(":")
                resultDict['registeredCode'] = b.lstrip(" ")
                #print "-> registeredCode is " + resultDict['registeredCode']
           #if i.find("netname:") != -1:
            #    a,b = i.split(":")
            #    resultDict['registeredCode'] = b.lstrip(" ") 
            if i.find("Source") != -1:
                a,b = i.split(":")
                resultDict['registry'] = b.lstrip(" ")
                #print "-> registry is " + resultDict['registry']
            if i.find("IP range") != -1:
                a,b = i.split(":")
                resultDict['netblock'] = b.lstrip(" ")
                #print "-> netblock is " + resultDict['netblock']
            # Pick up the first instance
            if i.find("Infos") != -1 and resultDict['info'] == "!":
                a,b = i.split(":")
                resultDict['info'] = b.lstrip(" ")
                #print "-> info is " + resultDict['info']
            # Search WHOIS "info" for keywords
            if i.find("Infos") != -1 :
                a,b = i.split(":")
                b=b.lstrip(" ").upper()
                if b.find("DSL") != -1 or b.find("SATELLITE") != -1 or b.find("PPP") != -1 or b.find("ULL") != -1 or  b.find("CUSTOMER") != -1 or  b.find("CORPORATE") != -1 or  b.find("ENTERPRISE") != -1 or b.find("DIAL") != -1 or b.find("ADSL") != -1 or b.find("3G") != -1 or b.find("POOL") != -1 or b.find("MOBILE") != -1 or b.find("STATIC") != -1 or b.find("UMTS") != -1  or b.find("BROADBAND") != -1 or b.find("HANDSET") != -1  or b.find("FIXED") != -1 or b.find("GPRS") !=-1 or b.find("GSM") != -1 :
                    resultDict['purpose'] = resultDict['purpose'].lstrip('?') + b + ","
                    #print "-> purpose is " + resultDict['purpose']    
            
            # Search WHOIS "info" for Vodafone-related keywords
            # todo : add search of registered name and abuse e-mail
            if i.find("Infos") != -1 :
                a,b = i.split(":")
                b=b.lstrip(" ").upper()
                if b.find("VODAFONE") != -1 or b.find("VF") != -1 or b.find("VFONE") !=-1 or b.find("ARCOR") !=-1 :
                    resultDict['vodafone'] = resultDict['vodafone'].lstrip('?') + b + ","
                    #print "-> vodafone is " + resultDict['vodafone']    
                
            if i.find("Abuse E-mail") != -1:
                a,b = i.split(":")
                resultDict['abuse'] = b.lstrip(" ")    
                #print "-> abuse is " + resultDict['abuse']            
        
        #print "ip2asn() : " + `resultDict`               

        resultDict['vodafone'] = resultDict['vodafone'].rstrip(',')
        resultDict['purpose']  = resultDict['purpose'].rstrip(',')

        # Prettify the known Vodafone Group AS names - keep to two digits if possible
        if resultDict['as'] == 'AS15502' : resultDict['registeredCode'] = "VF-IE"
        if resultDict['as'] == 'AS12663' : resultDict['registeredCode'] = "VF-SEDC"
        if resultDict['as'] == 'AS30722' : resultDict['registeredCode'] = "VF-IT"
        if resultDict['as'] == 'AS13083' : resultDict['registeredCode'] = "VF-DE"
        if resultDict['as'] == 'AS15480' : resultDict['registeredCode'] = "VF-NL"
        if resultDict['as'] == 'AS3209'  : resultDict['registeredCode'] = "VF-ARC"
        if resultDict['as'] == 'AS34419' : resultDict['registeredCode'] = "VF-GRP"	# VF Group
        if resultDict['as'] == 'AS25135' : resultDict['registeredCode'] = "VF-UK"
        if resultDict['as'] == 'AS12353' : resultDict['registeredCode'] = "VF-PT"
        if resultDict['as'] == 'AS21334' : resultDict['registeredCode'] = "VF-HU"
        if resultDict['as'] == 'AS12430' : resultDict['registeredCode'] = "VF-SP"
        if resultDict['as'] == 'AS12357' : resultDict['registeredCode'] = "VF-SP"	# Communitel - now part of VF Spain
        if resultDict['as'] == 'AS48728' : resultDict['registeredCode'] = "VF-QA"	# VF Qatar
                
        # Prepend tag for the known big Tier 1 AS
        if resultDict['as'] == 'AS3549'  : resultDict['registeredCode'] = "T1:GLOBAL-CROSSING"
        if resultDict['as'] == 'AS1239'  : resultDict['registeredCode'] = "T1:SPRINT"
        if resultDict['as'] == 'AS3356'  : resultDict['registeredCode'] = "T1:LEVEL3"
        
        # Prepend tag for the One Network transit providers - Colt
        if resultDict['as'] == 'AS5400'  : resultDict['registeredCode'] = "TR:BT"
        if resultDict['as'] == 'AS13237' : resultDict['registeredCode'] = "TR:LAMBDANET"
        # Prepend tag for the "Competitors"
        if resultDict['as'] == 'AS3125'  : resultDict['registeredCode'] = "COM:FT-ORANGE"
    
        return resultDict
    
    except Exception,e:
        #print "!!!!! ip2asn(): Caught exception for following raw data for IP=" + ip
        #print "command-line:" + cmdLine
        #print "raw data    :" + raw2
        #print "exception   :" + `e`
        syslog.syslog("ip2asn(): Caught exception = " + `e` + " for IP=" + ip) 
        return resultDict

# e.g. asn = 34419
def asn2routes(asn):
    resultSeq = [] 
    
    try:    
        # Classic case is 0.0.0.0
        #if not isPublicIP(ip):
        #    return resultDict

        cmdLine = "whois -B -i origin AS" + asn
        #print "cmdLine :",cmdLine

        pipe = os.popen(cmdLine,'r')
        raw = pipe.read()
        #print "raw=",raw
        #print "length of raw is " + `len(raw)`
        
        raw2 = raw.split('\n')
        #print "raw2=" + `raw2`

        for i in raw2:
            if i.find("route:") != -1 :
                a,b = i.split(":")
                b=b.lstrip()
                resultSeq.append(b.lstrip(" "))
            if i.find("origin:") != -1 :
                whoisAS = i.split(":")[1]
                whoisAS = whoisAS.lstrip()
                #print "whoisAS = " + whoisAS
                #print "asn     = " + asn
                if whoisAS != "AS" + asn :
                    raise Exception,"WHOIS route origin does not match expected"
                   
    except Exception,e:
        #print "!!!!! asn2routes(): Caught exception for following raw data for AS=" + asn
        #print "command-line:" + cmdLine
        #print "raw data    :" + raw2
        #print "exception   :" + `e`
        syslog.syslog("asn2routes(): Caught exception = " + `e` + " for AS=" + asn) 
            
    return resultSeq        
               
# put test harness here
if __name__ == "__main__" :

    routes = asn2routes("34419")
    print "routes = " + `routes`
  
    print "\ntest1\n-----"
    asInfo = ip2asnCymru("217.41.27.169")
    #print asInfo['registeredName']
    print asInfo['registeredCode']
    print asInfo['as']
    
    print "\ntest2\n-----"
    asInfo = ip2asnCymru("41.222.232.123")
    #print asInfo['registeredName']
    print asInfo['registeredCode']
    print asInfo['as']
    
    #if asInfo['error'] != None:
    #    print "ip2asn error : [" + asInfo['error'] + "]"
    #else:
    #    print asInfo    
    #
    #print "\ntest2\n-----"
    #asInfo = ip2asn("217.41.27.169",routes=1)
    #if asInfo['error'] != None:
    #    print "ip2asn error : [" + asInfo['error'] + "]"    
    #else:
    #    print asInfo    

#print "\ntest2\n-----"
#asInfo = ip2asn("1.1.1.1")
#if asInfo['error'] != None:
#    print "ip2asn error : [" + asInfo['error'] + "]"
#else:
#    print asInfo    
#print "\ntest3\n-----"
#if asInfo['error'] != None:
#    print "ip2asn error : [" + asInfo['error'] + "]"
#else:
#    print asInfo    
#
#print "\ntest4\n-----"
# a problem IP
#asInfo = ip2asn("216.152.254.248")
#if asInfo['error'] != None:
#    print "ip2asn error : [" + asInfo['error'] + "]"
#else:
#    print asInfo    
#
#print "\ntest5\n-----"
#asInfo = ip2asn("85.205.2.2")
#if asInfo['error'] != None:
#    print "ip2asn error : [" + asInfo['error'] + "]"
#else:
#    print asInfo    

# VF Italy
#print "\ntest6\n-----"
#asInfo = ip2asn("188.217.157.45")
#if asInfo['error'] != None:
#    print "ip2asn error : [" + asInfo['error'] + "]"
#else:
#    print asInfo    


    