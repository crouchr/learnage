#!/usr/bin/python

import time, sys, os , syslog , re 
import ipintellib

# return True if IP is to be ignored/hidden else return False
# ipAddress can be a string or a list of IP addresses

# This doesn't work well for apps in the cloud like Loggly where their IP just resolves to ec2-107-21-47-134.compute-1.amazonaws.com and they make 
# use of dynamipc DNS

def hiddenIP(ipAddress,lanAllowed=False) :
    
    try :
        #debug = True
        debug = False
        ipList = []

        HPOTS = ["192.168.1.50","192.168.1.60","192.168.1.61","192.168.1.62","192.168.1.63","192.168.1.64","192.168.1.65","192.168.1.66","192.168.1.68","192.168.1.69"]
        
        if isinstance(ipAddress,str) :
            ipList.append(ipAddress)
            #print "hiddenIP() : passed a STRING type"
        else:
            ipList = ipAddress
            #print "hiddenIP() : passed a LIST type"
        
        #print "kojoney_hiddenip.py : hiddenIP() : ipList = " + ipList.__str__()
                    
        for ip in ipList :       
            # check that IP is valid IP        
            pat = "(\d+\.\d+\.\d+\.\d+)"
            a = re.findall(pat,ip)
            if len(a) <= 0 :
                msg = "kojoney_hiddenip.py : hiddenIP() : error : " + ip + " is not a valid IP address, ipAddress=" + ipAddress.__str__()
                print msg
                #syslog.syslog(msg)	# THIS IS STILL A BUG
                #msg = "type of ipAddress is " + type(ipAddress)
                #syslog.syslog(msg)
                return False	# !!! ideally a third state would exist for errors
            #else:          
            #  print "hiddenIP() : lanAllowed : " + lanAllowed.__str__() + ", IP : " + ip.__str__()

            if ip == "127.0.0.1" :
                if debug == True :
                    syslog.syslog("hiddenIP(" + ip + "," + lanAllowed.__str__() + ") -> TRUE since ip is 127.0.0.1")
                return True
        
            # Google DNS
            if lanAllowed == False and ip == "8.8.8.8" :
                return True
        
            # BlackRain itself
            if lanAllowed == False and ip == "192.168.1.67" :
                return True
        
            # mail
            if lanAllowed == False and ip == "192.168.1.70" :
                return True
        
            # BRX
            if lanAllowed == False and ip == "192.168.1.90" :
                return True
        
            # Node called 'prelude' running VirtualBox
            if lanAllowed == False and ip == "192.168.1.73" :
                return True
            
            # Prelude SIEM 
            if lanAllowed == False and ip == "192.168.1.74" :
                return True
            
            # Spade/Snort external sensor
            if lanAllowed == False and ip == "192.168.1.76" :
                return True
            
            # DSL node
            if lanAllowed == False and ip == "192.168.1.254" :
                return True
            
            # Cloud node itself
            if lanAllowed == False and ip == "192.168.1.93" :
                return True

            if ip in HPOTS:	
                continue    	
             
            #print "slow processing code entered for IP = " + ip.__str__()        
            # Sometimes LAN IPs are allowed, othertimes not - so cater for both cases
            #if lanAllowed == False and ip.find("192.168.1.") != -1 :
            #    if debug == True :
            #        syslog.syslog("hiddenIP(" + ip + "," + lanAllowed.__str__() + ") -> TRUE at LAN check")
            #        print ip + " should be hidden"
            #    return True

            dnsInfo = ipintellib.ip2name(ip)
            dnsName = dnsInfo['name'].rstrip('.')
            #print "kojoney_hiddenip.py : " + dnsName.__str__()


            # ignore traffic from Internet test hosts
            #if ip.find("173.203.89.") != -1 :	# GSOC slice server roy.doesntexist.org 
            #    if debug == True :
            #        syslog.syslog("hiddenIP(" + ip + "," + lanAllowed.__str__() + ") -> TRUE , DNS = slice server doesntexist.org")
            #    return True

            # ignore traffic from Google DNS
            if ip.find("8.8.8.8") != -1 :	 
                #if debug == True :
                #syslog.syslog("hiddenIP(" + ip + "," + lanAllowed.__str__() + ") -> TRUE , DNS = slice server doesntexist.org")
                return True

            # ignore traffic associated with Twitter
            if dnsName.find("twttr.com") != -1 :
                if debug == True :
                    syslog.syslog("hiddenIP(" + ip + "," + lanAllowed.__str__() + ") -> TRUE , DNS = twttr.com")
                return True    
        
            # ignore traffic associated with updating Slackware patches
            if dnsName.find("slackware.mirrors") != -1 :
                if debug == True :
                    syslog.syslog("hiddenIP(" + ip + "," + lanAllowed.__str__() + ") -> TRUE , DNS = slackware.mirrors")
                return
        
            # ignore traffic associated with malware analysis by Anubis at Univ California Santa Barbara
            if dnsName.find("anubis.cs.ucsb.edu") != -1 :
                if debug == True :
                    syslog.syslog("hiddenIP(" + ip + "," + lanAllowed.__str__() + ") -> TRUE , DNS = anubis.cs.ucsb.edu")
                return
            
            # ignore traffic associated with honeyd updating it's site
            if dnsName.find("honeyd.provos.org") != -1 :
                if debug == True :
                    syslog.syslog("hiddenIP(" + ip + "," + lanAllowed.__str__() + ") -> TRUE , DNS = honeyd.provos.org")
                return True    

            # ignore traffic associated with Team Cymru
            if dnsName.find("cymru.com") != -1 :
                if debug == True :
                    syslog.syslog("hiddenIP(" + ip + "," + lanAllowed.__str__() + ") -> TRUE , DNS = cymru.com")
                return True    

            # Filter based on AS number / name - do last since expensive lookup
            asInfo = ipintellib.ip2asn(ip) 
            asNum = asInfo['as']		                                # AS123   
            asRegisteredCode = asInfo['registeredCode'].upper()                 # e.g. GOOGLE
            #print "kojoney_hiddenip.py : " + asRegisteredCode.__str__()
            
            if asRegisteredCode.find("GOOGLE") != -1 :
                if debug == True :
                    syslog.syslog("hiddenIP(" + ip + "," + lanAllowed.__str__() + ") -> TRUE , AS = GOOGLE")
                return True
 
            if asRegisteredCode.find("TWITTER-NETWORK") != -1 :
                if debug == True :
                    syslog.syslog("hiddenIP(" + ip + "," + lanAllowed.__str__() + ") -> TRUE , AS = TWITTER-NETWORK")
                return True

            if asRegisteredCode.find("FACEBOOK") != -1 :
                if debug == True :
                    syslog.syslog("hiddenIP(" + ip + "," + lanAllowed.__str__() + ") -> TRUE , AS = FACEBOOK")
                return True

            # ip is an attacker    
            if debug == True :
                syslog.syslog("hiddenIP(" + ip + "," + lanAllowed.__str__() + ") -> FALSE, ip is an attacker")

            #return False

        return False
        
    except Exception,e:
        msg = "kojoney_hiddenip.py : hiddenIP() : exception " + `e` + " ip=" + ipAddress.__str__()
        print msg
        syslog.syslog(msg)
        return None
                               
# -------------------------------------------------------
        
# Start of code
# This is a test harness so comment/uncomment the relevent lines        
        
if __name__ == '__main__' :
    
    # Test : nonsense input   
    result = hiddenIP("not a valid IP")	
    print "hiddenIP() -> " + result.__str__()


    IPLIST = "1.2.3.4"
    result = hiddenIP(IPLIST)	
    print "hiddenIP() -> " + IPLIST.__str__() + " => " + result.__str__()
 

    IPLIST = ["1.2.3.4"]
    result = hiddenIP(IPLIST)	
    print "hiddenIP() -> " + IPLIST.__str__() + " => " + result.__str__()
    
    IPLIST = ["1.2.3.4","6.6.6.6"]
    result = hiddenIP(IPLIST)	
    print "hiddenIP() -> " + IPLIST.__str__() + " => " + result.__str__()
         
    # Test : Set the input file to scan
    filename = 'test_hiddenip.txt'
    file = open(filename,'r')

    while True:
    
        # Tweets log file       
        # where = file.tell()
        line  = file.readline()
        ip    = line.rstrip('\n')
        
        if not line:				# no data to process
            sys.exit()
        else :					# new data has been found
            result = hiddenIP(ip)		# LAN allowed = False
            print "hiddenIP(" + ip + ") -> " + `result`
        
        #if msg != None:
        #    print "*** Tweet : " + msg
                       
        #print "sleeping..."
        # this can be a float for sub-second sleep    
        time.sleep(0.1)		# 0.1 
                              
                 