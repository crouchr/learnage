#!/usr/bin/python
#/usr/local/bin/python
# 
# This program is used to gather info from the user and then
# send this data to the BRX for registration
# It should only be necessary to run this program once
# In this version, it assumes that an IP address has been provided
# by a DHCP server on the LAN

# This version is for use on the honeytweeter node , mars

sensorVersion   = "b-rc2"	# change per CD release - i.e. when any file changes
registerVersion = "v0.1"	# change when this file changes 

# standard Python libraries
import time,sys,logging

# rch libraries
import blackrain_stun
import blackrain_mac
import blackrain_ipintellib
import blackrain_default_gw
import blackrain_cpuinfo
import blackrain_logging

# third-party libraries
import BlackRainClient				# Mat's API to BRX

# Permanently Hard-coded values
# =============================
brxName  = "rocknroll.dyndns-server.com"	# fake this by putting it in local /etc/hosts file
brxPort  = "743"
pingHost = "www.google.com"
#pingHost = "www.dqewqwe2331oogle.com"		# force a fail - host does not exist

# Temporary hard-coded values
# ===========================
sensorCPUnum   = 1				# faked : not in /proc/cpuinfo ?

try:

    blackrain_logging.setLogging(mode='a')
    logging.info("Started, registerVersion=" + registerVersion + ", sensorVersion=" + sensorVersion)
    
    # Until BRX is always up, then do not abort if can't ping it 
    #a = blackrain_default_gw.doHaveConnectivity(brxName) 
    #if a == False:
    #    msg = "Failed to ping BRX, host=" + brxName
    #    logging.critical(msg)

    a = blackrain_default_gw.doHaveConnectivity(pingHost) 
    if a == False:
        msg = "Aborting, failed to configure connectivity to Internet, testHost=" + pingHost
        logging.critical(msg)
        print msg
        sys.exit()

    # Uncomment the following to test exception handling
    #print "a" + None
    #print 8/0

    # Determine host CPU capabilities
    cpuinfo = blackrain_cpuinfo.getCpuInfo()
    if cpuinfo != None :       
        sensorCPUbogomips = cpuinfo['bogomips']
        sensorCPUfreq     = cpuinfo['cpuMHz']
        sensorCPUmodel    = cpuinfo['modelName']
        sensorCPUflags    = cpuinfo['cpuflags']
    
        a = "sensorID (bogomips)  = " + sensorCPUbogomips.__str__()
        logging.info(a)
        a = "sensorID (cpuMhz)    = " + sensorCPUfreq.__str__()
        logging.info(a)
        a = "sensorID (modelName) = " + sensorCPUmodel.__str__()
        logging.info(a)
        a = "sensorID (cpuflags)  = " + sensorCPUflags.__str__()
        logging.info(a)
    
    meminfo = blackrain_cpuinfo.getCpuMem()
    if meminfo != None :       
        sensorCPUmemtotal = meminfo['memtotal'].__str__()
        sensorCPUmemfree  = meminfo['memfree'].__str__()
    
        a = "sensorID (memtotal)  = " + sensorCPUmemtotal.__str__()
        logging.info(a)
        a = "sensorID (memfree)   = " + sensorCPUmemfree.__str__()
        logging.info(a)
        
    # Determine default GW for this LAN
    sensorDGip,sensorDGiface = blackrain_default_gw.getDGIP()
    
    if sensorDGip != None and sensorDGiface != None:
        a = "Default Gateway IP : " + sensorDGip.__str__()
        #print a
        logging.info(a)
        a = "Default Gateway reachable via : " + sensorDGiface.__str__()
        #print a
        logging.info(a)
                                
        sensorDGmac = blackrain_default_gw.getMACip(sensorDGip)
        if sensorDGmac != None :
            a = "Default Gateway MAC : " + sensorDGmac.__str__()
            logging.info(a)
    else:
        a = "Failed to determine this LAN's default gateway, sensorDGip=" + sensorDGip.__str__() + ", sensorDGiface=" + sensorDGiface.__str__()
        print a
        logging.critical(a)
        sys.exit()

    # Determine sensor host MAC address - needs interface to be up
    mac = blackrain_mac.getMacAddress(sensorDGiface)
    msg = "MAC address = " + mac.__str__()
    logging.info(msg)
    
    sensorId = mac.replace(":","")	# remove the colons
    #sensorId = "6cf04956bfba"		# hard-coded until in database
    
    if mac == None:
        a = "No ethernet interfaces found in UP state, sensorDGiface=" + sensorDGiface.__str__()
        print a
        logging.critical(a)
        sys.exit()
    else:    
        a = "sensorID = " + sensorId.__str__()
        logging.info(a)

    #print "\n"
    print "+-------------------------------+"
    print "| BlackRain Sensor Registration |"
    print "+-------------------------------+"
    print " "
    print "version : " + sensorVersion
    print " "
    print "Thank you for participating in the BlackRain Honeynet Project"
    print "Remember : All your honeypots are belong to us !"
#    print " "
#    print "Note : You must be running DHCP on your LAN"
    print " "
    print "Only information marked with a * will appear on the BlackRain public website"
    print "BlackRain website : http://blackrain.org [tbd]"
    print " "
    print "If you experience problems, please e-mail honeytweeter@gmail.com for help."
    print " "
    print "Your equipment details"
    print "----------------------"
    print "sensor MAC address                : " + mac
    print "sensor ID                         : " + sensorId
    print "sensor ethernet interface         : " + sensorDGiface 
    print "IP  address of default gateway    : " + sensorDGip 
    print "MAC address of default gateway    : " + sensorDGmac 
    print " "
    print "Your details"
    print "-------------"
    sensorPersonName   = raw_input("Your name                         : ")
    sensorName         = raw_input("BlackRain Sensor name*            : ")
    sensorPersonEmail  = raw_input("Contact e-mail address            : ")
    sensorReportsEmail = raw_input("BlackRain Reports e-mail address  : ")
    print " "
    #print "Your sensor's customisation"
    #print "---------------------------"
    #honeydIP   =  raw_input("HONEYD honeypot IP address        : ")
    #amunIP     =  raw_input("AMUN honeypot IP address          : ")
    #kippoIP    = raw_input("Enter the static IP to be used by the KIPPO honeypot    : ")
    #glastopfIP = raw_input("Enter the static IP to be used by the GLASTOPF honeypot : ")

    #honeypotIPList = "honeydIP=" + honeydIP.__str__() + ",amunIP=" + amunIP.__str__()
    #a = "list of honeypot IPs : " + honeypotIPList.__str__()
    #logging.info(a)

    print " "
    print "Press RETURN   to confirm that this data is correct"
    a = raw_input("Press <Ctrl>-C to abort and re-run the registration process ")

    print "\nGathering installation-specific data..."
                            
    # Determine sensor host public IP address using STUN protocol
    # Put a retry loop of 3 attempts in here - it failed on me at least once
    print "[+] Determining your public IP address (may take upto 30 seconds)..."
    natType , wanIP = blackrain_stun.getExternalIP()
    a = "WAN IP = " + wanIP.__str__()
    logging.info(a)
    a = "NAT Type = " + natType.__str__()
    logging.info(a)

    if wanIP == None:
        logging.critical("Failed to determine public IP")
        print "Unable to determine your public IP address"
        print "This may be a temporary issue so maybe retry in an hour"
        sys.exit()
             
    # Make network calls to gather DNS and WHOIS information
    print "[+] Determining your ISP information..."
    dnsInfo = blackrain_ipintellib.ip2name(wanIP)
    dnsName = dnsInfo['name'].rstrip('.')                   # right-strip the trailing .
    a = "DNS-derived info " + dnsInfo.__str__()      
    print a
    logging.info(a)
                            
    # WHOIS         
    asInfo = blackrain_ipintellib.ip2asn(wanIP)                       # 
    asNum = asInfo['as']                                    # AS123   
    asRegisteredCode = asInfo['registeredCode']             # Short-form e.g.ARCOR
    a = "whois-derived info " + asInfo.__str__()
    print a
    logging.info(a)
                                                             
    # GeoIP information - faster than WHOIS for looking up Country Code information
    # Need good error checking on this - can BRX handle a "None" in a field in push registration ?
    geoIP = blackrain_ipintellib.geo_ip(wanIP)
    countryCode = geoIP['countryCode']                                                   
    countryName = geoIP['countryName']                                                   
    city        = geoIP['city']
    longitude   = geoIP['longitude']                         # Used to calc approx. localtime
    latitude    = geoIP['latitude']
    a = "geoIP-derived info " + geoIP.__str__()
    print a
    logging.info(a)

    # fill the registration info message structure 
    sensorRegistration = {}
    sensorRegistration["sensorId"]              = sensorId
    sensorRegistration["sensorVersion"]         = sensorVersion
    sensorRegistration["sensorWanIP"]           = wanIP
    sensorRegistration["sensorName"]            = sensorName
    sensorRegistration["sensorPersonName"]      = sensorPersonName
    sensorRegistration["sensorPersonEmail"]     = sensorPersonEmail
    sensorRegistration["sensorReportsEmail"]    = sensorReportsEmail	# AMUN uses this to send Anubis analysis
    sensorRegistration["sensorDGiface"]         = sensorDGiface		
    sensorRegistration["sensorDGmac"]           = sensorDGmac		# so we know default gateway manufacturer (NAT instructions)
    sensorRegistration["sensorBaseIPmethod"]    = "dhcp"		# this is the only option at the moment, "static" is a future
    #sensorRegistration["sensorHoneypotIPList"]  = honeypotIPList 
    sensorRegistration["sensorNatType"]         = natType
    sensorRegistration["sensorIPCountryCode"]   = countryCode
    sensorRegistration["sensorIPCountryName"]   = countryName
    sensorRegistration["sensorIPCityName"]      = city
    sensorRegistration["sensorIPLatitude"]      = "%.2f" % latitude		
    sensorRegistration["sensorIPLongitude"]     = "%.2f" % longitude
    sensorRegistration["sensorIPASN"]           = asNum
    sensorRegistration["sensorIPASName"]        = asRegisteredCode
    sensorRegistration["sensorIPDNS"]           = dnsName
    sensorRegistration["sensorCPUnum"]          = sensorCPUnum
    sensorRegistration["sensorCPUmodel"]        = sensorCPUmodel
    sensorRegistration["sensorCPUfreq"]         = sensorCPUfreq
    sensorRegistration["sensorCPUflags"]        = sensorCPUflags
    sensorRegistration["sensorCPUbogomips"]     = sensorCPUbogomips
    sensorRegistration["sensorCPUmemtotal"]     = sensorCPUmemtotal
    sensorRegistration["sensorCPUmemfree"]      = sensorCPUmemfree
    sensorRegistration["sensorSSL"]             = "1"		# User wants to use SSL		
    sensorRegistration["sensorRAM"]             = "0"		# This field is not needed
    sensorRegistration["sensorUptime"]          = 0		# This field is not needed

    a = "sensorRegistration info " + sensorRegistration.__str__()
    logging.info(a)

    # Do some basic sanity checking 
    # #0 Do the names have a minimum length of 3 characters ?
    # #1 is there '@' and '.' in the email address ?
    # #2 do all the supplied IP addresses look like IP addresses ?
    # #3 are all the supplied IP addresses different ?
    # #4 are the data entered by user shorter than 32 characters long and trucate
    # if necessary

    # Register the sensor with the BRX
    # ================================

    # Lookup IP using /etc/hosts file first (local override for testing)
    #a = "BRX DNS name     : " + brxName.__str__()
    #logging.info(a)
    #a = "BRX port number  : " + brxPort.__str__()
    #logging.info(a)
    #
    #brxIP = blackrain_ipintellib.name2ipHosts(brxName)
    #if brxIP != None :
    #    logging.info("BRX DNS name found in /etc/hosts")    
    #else:
    #    dnsInfo = blackrain_ipintellib.ip2name(brxName)	    # Use DNS server for DNS to IP
    #    brxIP = dnsInfo['name'].rstrip('.')                 # right-strip the trailing .
    #    logging.info("BRX DNS name found via Internet DNS")    
    brxIP   = "192.168.1.92"	# hardcoded
    brxPort = "8080"		# hardcoded
    a = "BRX IP address   : " + brxIP.__str__()
    logging.info(a)

    # Contact the BRX and push our registration information
    brapi = BlackRainClient.BlackrainAPI(brxIP,brxPort,sensorId)

    a = "API version : v" + brapi.get_version()
    logging.info(a)

    # establish a session to BRX
    print "Establishing session to BRX..."
    responseFromBrapi = brapi.establish_session()

    if responseFromBrapi != BlackRainClient.BlackrainConnectStatus.ACCESS_SUCCESS:
        a = "Establish session to BRX FAILED : response = " + responseFromBrapi.__str__()
        print a
        logging.critical(a)
        sys.exit()
    else :        
        a = "Establish session to BRX was SUCCESSFUL : response = " + responseFromBrapi.__str__()
        print a
        logging.info(a)
            
    # send registration details to BRX    
    responseFromBrapi = brapi.push_registration_details(sensorRegistration)
    
    if responseFromBrapi != BlackRainClient.BlackrainConnectStatus.PUSH_OK:
        a = "Push registration data to BRX FAILED : response = " + responseFromBrapi.__str__()
        print a
        logging.critical(a)
        sys.exit()
    else :	
        a = "Push registration data to BRX : response = " + responseFromBrapi.__str__()
        print a
        logging.info(a)
                
    # Report result to user
    print "Congratulations !"
    print "Your sensor " + '"' + sensorName + '"' + " has been successfully registered with the BlackRain Honeynet"
    #print " "
    #print "Now you need to enable port forwarding/DMZ on your DSL/Firewall/Router as follows :-"
    #print "1. Set the following IP as the DSL/Firewall/Router 'DMZ' : " + honeydIP
    #print "2. FTP malware downloads to : "  + amunIP     + " , ports = tcp62001 to tcp62003"
    #print "3. Win32 attacks to         : "  + amunIP     + " , ports = tcp135 tcp445 + <more here>..."
    #print "4. Web-server attacks to    : "  + glastopfIP + " , ports = tcp80 tcp8080"
    #print "5. Forward the following port(s) to "  + kippoIP +    " : tcp22"
    print " "
    print "Happy Honeypotting !" 
    print " "
    print "The BlackRain Development Team"
    print " "

    logging.info("Finished")
    
except Exception,e :
    a = "Exception " + e.__str__() + " in register-simple.py main()"
    print a
    logging.critical(a)
        