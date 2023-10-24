#!/usr/bin/python

import time, os , syslog , urlparse 
import twitter		# Google API

import ipintellib	# RCH library 
import mailalert	# RCH library
import p0fcmd		# RCH library - master on mars

# Globals
PreviousIPs = {}
CLInum=0		# number of lines of CLI processed
Version="1.2"		# added p0f v 3.0.0
TweetVersion="0.2"	# update if Tweet format changes
SessionId=-1		# incremented for every authenticated (authOK) session
Username = "_unknown_"	# Uninitialised

# need this so program can be monitored by monit
# make this a library function
def makePidFile(name):
    pid = os.getpid()
    
    pidFilename = "/var/run/rchpids/" + name + ".pid"
    fp=open(pidFilename,'w')
    print >> fp,pid
    fp.close()            
    #print "pid is " + `pid`
    return pid	# returns None if failed
                        
# Send an e-mail
def alert(subject,ip,username,content):
    smtpServer   = 'smtp.btconnect.com'
    sender       = 'the.crouches@btconnect.com'
    destination  = ['richard.crouch@vodafone.com']
    debugLevel   = False
    
    try:
        # Get DNS info
        dnsInfo = ipintellib.ip2name(ip)
        dnsName = dnsInfo['name']
        
        # WHOIS information
        asInfo = ipintellib.ip2asn(ip)
        asNum = asInfo['as']					# AS123 
        asRegisteredCode = asInfo['registeredCode']		# Short-form e.g.ARCOR
        
        # GeoIP information
        geoIP = ipintellib.geo_ip(ip)
        countryCode = geoIP['countryCode']
        city        = geoIP['city']
        longitude   = geoIP['longitude']			# Calc approx. localtime
        latitude    = geoIP['latitude']    
                    
        info = "haxx0r IP : " + ip + "\nuser : " + username + "\nDNS : " + dnsName + "\n\nAS Number : " + asNum + "\nAS Name : " + asRegisteredCode + "\n\nGeoIP Country : " + countryCode + "\nGeoIP City : " + "\nGeoIP Longitude : " + "%.2f" % longitude + "\nGeoIP Latitude : " + "%.2f" % latitude 
   
        # Haxx0r's client stack information
        p0fInfo = p0fcmd.getP0fInfo(ip,"0","172.31.0.67","22");
        if p0fInfo['result'] == True:
             p0fStr = "os=" + p0fInfo['genre'] + " hops=" + p0fInfo['hops'] + " linktype=" + p0fInfo['linktype'] + " up_secs=" + p0fInfo['uptime'] + " tos=" + p0fInfo['tos'] + " masq=" + p0fInfo['masq'] + " fw=" + p0fInfo['firewall'] + " NAT=" + p0fInfo['nat'] + " realOS=" + p0fInfo['realos']
        else:
             p0fStr = p0fInfo['errormsg']
   
        # Notify !
        alertSubject = "honeypot intrusion! : " + subject
        alertContent = info + "\n\np0f : " + p0fStr + "\n\n" + content + "\n\nSent by Kojoney Honeypot\n\n"                 
        
        print "alert():\nsubject:" + alertSubject + "\ncontent:\n" + alertContent + "\n"

        status = mailalert.mailalert(sender,destination,smtpServer,alertSubject,alertContent,debugLevel)
    
        # Add a record to syslog
        a = "Sent alert e-mail, Subject=" + alertSubject + " to " + destination[0]
        syslog.syslog(a)
    
    except Exception,e:
        syslog.syslog("kojoney_tail.py : alert() : " + `e` + " ip=" + ip)

def statusAlert(subject,content):
    smtpServer   = 'smtp.btconnect.com'
    sender       = 'the.crouches@btconnect.com'
    destination  = ['richard.crouch@vodafone.com']
    debugLevel   = False
    
    try:
        
        # Notify !
        alertSubject = "honeypot status : " + subject
        alertContent = content + "\n\nSent by Kojoney Honeypot\n\n"                 
        
        #print "alert subject:" + alertSubject + "\nalertContent:\n" + content + "\n"

        status = mailalert.mailalert(sender,destination,smtpServer,alertSubject,alertContent,debugLevel)
    
        # Add a record to syslog
        a = "Sent alert e-mail, Subject=" + alertSubject + " to " + destination[0]
        syslog.syslog(a)
    
    except Exception,e:
        syslog.syslog("kojoney_tail.py : statusAlert() : " + `e`)


# Write Security Visualisation data to be processed by AfterGlow to .csv file
# Format : IP_address,commandStr
# Need to touch this file
# TODO : add boot time epoch hours to output file as a way of tracking commands entered by a single haxx0r
def writeSecViz1(ip,username,countryCode,commandStr):
    try:    
        p0fInfo = p0fcmd.getP0fInfo(ip,"0","172.31.0.67","22");
        if p0fInfo['result'] == True:
            p0fStr = "os:" + p0fInfo['genre'] + ":hops=" + p0fInfo['hops'] 
        else:
            p0fStr = p0fInfo['errormsg']
        
        #raise Exception	# test code
        #print i		# force exception for testing
        
        asInfo = ipintellib.ip2asn(ip)
        asNum = asInfo['as']				        # AS123 
        asRegisteredCode = asInfo['registeredCode']		# Short-form e.g.ARCOR
    
        fpOut = open(r'/var/log/kojoney_tail_secviz_cmds.csv','a')
        
        msg = ip + ":" + asNum + ":" + asRegisteredCode + ":" + p0fStr + "," + username + "," + '"' + commandStr + '"' + "," + countryCode  
        print "writeSecViz1():" + msg
        print >> fpOut,msg
        fpOut.close()
        
    except Exception,e:
        syslog.syslog("kojoney_tail.py : writeSecViz1() exception caught = " + `e` + " ip=" + ip)

# Write Security Visualisation data to be processed by AfterGlow to .csv file
# Format IP_address,commandStr
# Need to touch this file
def writeSecViz2(ip,username,countryCode,fileName):
    try:    
        p0fInfo = p0fcmd.getP0fInfo(ip,"0","172.31.0.67","22");
        if p0fInfo['result'] == True:
            p0fStr = "os:" + p0fInfo['genre'] + ":hops=" + p0fInfo['hops'] 
        else:
            p0fStr = p0fInfo['errormsg']
    
        asInfo = ipintellib.ip2asn(ip)
        asNum = asInfo['as']					# AS123 
        asRegisteredCode = asInfo['registeredCode']		# Short-form e.g.ARCOR
    
        fpOut = open(r'/var/log/kojoney_tail_secviz_dloads.csv','a')
        
        msg = ip + ":" + asNum + ":" + asRegisteredCode + ":" + p0fStr + "," + username + "," + fileName + "," + countryCode
        print "writeSecViz2():" + msg
        print >> fpOut,msg
        fpOut.close()

    except Exception,e:
        syslog.syslog("kojoney_tail.py : writeSecViz2() exception caught = " + `e` + " ip=" + ip)

# Write Security Visualisation data to be processed by AfterGlow to .csv file
# This file is used for correlating haxx0r IP stack uptime with username and src IP
# Need to touch this file
# add hops ?
def writeSecViz3(ip,username):

    #print "entered writeSecViz3()"
    now = time.time()
    
    try:    
        p0fInfo = p0fcmd.getP0fInfo(ip,"0","172.31.0.67","22");
        if p0fInfo['result'] == True :		# p0f data is available
            hops = p0fInfo['hops']
            os   = p0fInfo['genre']
            fw   = p0fInfo['firewall']
            nat  = p0fInfo['nat'] 
            if p0fInfo['genre'] == "Linux" :
                uptime = p0fInfo['uptime'] 
                bte = now - int(uptime)
                hops = p0fInfo['hops']    
            else:
                uptimeHours = 0
                bte = 0
        else:					# p0f data not read OK
            hops = 0        
            os   = "?"
            fw   = "?"
            nat  = "?"
            bte  = 0
              
        # get current time
        timeTuple = time.localtime(now)
        nowStr    = time.asctime(timeTuple)
            
        # calc haxx0r bootTime 	
        timeTuple   = time.localtime(bte)
        bootTimeStr = time.asctime(timeTuple)
        bootTimeEpochHours = int(bte/3600)
        #print "bootTimeEpochHours:" + `bootTimeEpochHours`
        
        asInfo = ipintellib.ip2asn(ip)
        #asNum = asInfo['as']					# AS123 
        asRegisteredCode = asInfo['registeredCode']		# Short-form e.g.ARCOR
        
        msg = ip + "," + `bootTimeEpochHours` + "," + ip + ":" + Username + "," + "os=" + os + ",hops=" + hops + ","\
        + asRegisteredCode + ",now=" + nowStr + "," + `now` + ",bootTime=" + bootTimeStr + "," + `bte` + ",fw=" + fw + ",nat=" + nat
        
        print "WriteSecViz3() = " + msg
        
        fpOut = open(r'/var/log/kojoney_tail_secviz3_uptime.csv','a')
        print >> fpOut,msg 
        fpOut.close()

    except Exception,e:
        syslog.syslog("kojoney_tail.py : writeSecViz3() exception caught = " + `e` + " ip=" + ip)


# Send a Tweet from  honeytweeter
# username is actually the global variable Username
def sendTweetCLI(sessionid,username,ip,cli):
    global TweetClient
    global TweetVersion			# bump version of format of Tweet changes
        
    print "Entered sendTweetCLI()"
    
    now=time.time()
    
    try:
        # sessionid of -1 indicates that we have no AUTH_OK event and so no username - so don't tweet it
        if (int(sessionid) < 0):
            print "sessionId < 0 -> no previous AUTH_OK event to get username"
            return
    
        p0fInfo = p0fcmd.getP0fInfo(ip,"0","172.31.0.67","22");
        if p0fInfo['result'] == True :		# p0f data is available
            hops = p0fInfo['hops']
            os   = p0fInfo['genre']
            fw   = p0fInfo['firewall']
            nat  = p0fInfo['nat'] 
            if p0fInfo['genre'] == "Linux" :
                uptime = p0fInfo['uptime'] 
                bte = now - int(uptime)		# boot time (epoch secs)
                hops = p0fInfo['hops']    
            else:
                uptimeHours = 0
                bte = 0
        else:					# p0f data not read OK
            hops = 0        
            os   = "?"
            fw   = "?"
            nat  = "?"
            bte  = 0
                  
        # get current time
        timeTuple = time.localtime(now)
        nowStr    = time.asctime(timeTuple)
            
        # calc haxx0r bootTime 	
        #timeTuple   = time.localtime(bte)
        #bootTimeStr = time.asctime(timeTuple)
        bteh = int(bte/3600)	# bteh = boot time epoch (hours)
        
        # Get DNS info
        dnsInfo = ipintellib.ip2name(ip)
        dnsName = dnsInfo['name']
        
        # WHOIS information
        asInfo = ipintellib.ip2asn(ip)
        asNum = asInfo['as']					# AS123 
        asRegisteredCode = asInfo['registeredCode']		# Short-form e.g.ARCOR
        
        # GeoIP information
        geoIP = ipintellib.geo_ip(ip)
        countryCode = geoIP['countryCode']
        city        = geoIP['city']
        longitude   = geoIP['longitude']			# Used to calc approx. localtime
        
        # Compact usual returns
        if asNum.find("AS-none")!= -1 :
            asNum="?"
        if asRegisteredCode.find("failed")!= -1 :
            asRegisteredCode="?"
        if countryCode.find("None") != -1 :
            countryCode="?"
        if city.find("None") != -1 :
            city="?"
            
        # Construct Tweet
        # todo - if os = windoes, do not add bteh
        msg = "sid=" + `sessionid` + ":IP=" + ip + ":" + asNum + "(" + asRegisteredCode + ")" + ":"\
        + countryCode + ":" + city + ":" + "%.2f" % longitude + ":" + os + ":" + hops\
        + ":fw=" + fw + ":nat=" + nat + ":bteh=" + `bteh`\
        + ":" + username + "@hpot $ " + cli

        # Send the Tweet - max = 147 ?        
        syslog.syslog("sendTweetCLI(): msg length=" + `len(msg)` + " chars")
        print "Tweet=" + msg
        
        # syslog every Tweet attempted to be sent    
        syslog.syslog("sendTweetCLI(): " + msg)
        
        # *** Disable during testing *** 
        status = TweetClient.PostUpdate(msg)
        time.sleep(5)		# crude rate-limit ?        
    
    except Exception,e:
        syslog.syslog("kojoney_tail.py : sendTweetCLI() exception caught = " + `e` + " ip=" + ip)

# Send a Tweet from honeytweeter for interesting Snort events
def sendTweetSnort(event):
    global TweetClient
    #global TweetVersion			# bump version of format of Tweet changes
        
    print "Entered sendTweetSnort()"
    
    try:
            
        # Construct Tweet
        msg = "ids:" + event
        
        # Send the Tweet - max = 147 chars ?        
        syslog.syslog("sendTweetSnort(): msg length=" + `len(msg)` + " chars")
        print "Tweet=" + msg
        
        # syslog every Tweet attempted to be sent    
        syslog.syslog("sendTweetSnort(): " + msg)
        
        # *** Disable during testing *** 
        status = TweetClient.PostUpdate(msg)        
        time.sleep(5)
    
    except Exception,e:
        syslog.syslog("kojoney_tail.py : sendTweetSnort() exception caught = " + `e`)


# Send a Tweet from honeytweeter for interesting netflow events
def sendTweetFlow(event,flow):
    global TweetClient
    #global TweetVersion			# bump version of format of Tweet changes
        
    print "Entered sendTweetFlow()"
    
    try:
            
        # Construct Tweet
        msg = "netflow:" + event + ":" + flow
        
        # Send the Tweet - max = 147 chars ?        
        syslog.syslog("sendTweetFlow(): msg length=" + `len(msg)` + " chars")
        print "Tweet=" + msg
        
        # syslog every Tweet attempted to be sent    
        syslog.syslog("sendTweetFlow(): " + msg)
        
        # *** Disable during testing *** 
        status = TweetClient.PostUpdate(msg)        
        time.sleep(5)
        
    except Exception,e:
        syslog.syslog("kojoney_tail.py : sendTweetFlow() exception caught = " + `e`)


# cliNum is ignored 
# set ip="0" if not relevant
def makeMsg(cliNum,ip,msg):
    now =time.time()
    timeTuple= time.localtime(now)
    
    # create the complete log entry text
    a = time.asctime(timeTuple) + "," + Version + "," + ip + "," + "%06d" % SessionId + "," + msg
    
    #print a 
    fpOut = open(r'/home/var/log/kojoney_tail.log','a')
    #syslog.syslog(a)
    print >> fpOut,a
    fpOut.close()

# 15 degrees = 1 hour - rounded down
# this needs unit testing
def calcLocalTime(longitude):
    if int(longitude) > 360 :	# GeoIP returns 999.0 if failed
        offsetSecs = 0;
    else:    
        offsetSecs = 3600 * int(longitude / 15)
    
    now = time.time()
    localTime = now + int(offsetSecs)
    
    #print "offsetSecs        : " + `offsetSecs`
    #print "localTime (epoch) : " + `localTime`
    timeTuple = time.localtime(localTime)
    #print "localTime         : " + time.asctime(timeTuple)
    
    return time.asctime(timeTuple)

# calculate haxx0r PC boot time in "My Time"      
# uptime is string - uptime in seconds - assumes p0f v3.0.0 is running
# uptime could be '?' e.g. if from a Windows box
# setting boottime to 0 indicates bootime is not valid

def calcBootTime(uptime):
    bootTime = {}
        
    now = time.time()			# epoch seconds
    if uptime == '?':			# probably Windows box    
        bte = 0
    else:  
        bte = now - int(uptime)
         	
    bootTime['epoch'] = `bte`
    #print "bootTime['epoch'] = " + `bootTime['epoch']`
    
    timeTuple = time.localtime(bte)
    bootTime['timeStr'] = time.asctime(timeTuple)
    #print "bootTime['timeStr'] = " + time.asctime(timeTuple)
    
    # record time of last visit by this IP
    bootTime['lastVisit'] = `now`
    timeTuple = time.localtime(now)
    bootTime['lastVisitStr'] = time.asctime(timeTuple) 
    
    return bootTime 
                           
# return True is backspace or Up arrow etc. are pressed indicated a human
# TODO : send an email 
def isHuman(cliList):
    for x in cliList:
        if (x.find('\x7f') != -1) or (x.find('\x1b') != -1):
            return True
    return False    

# Process Snort log entries
# Look for initial reconnaisance
#vi.e. NMAP pings etc
# TODO : add Nmap scan but only if dest is 172.31.0.67:22
# TODO : dump never seen before messages to a text file
def processSnort(line):
            
    print "processSnort() : line read from Snort file : " + line + "\n"
        
#   if line.find("172.31.0.67:22") != -1 or line.find('172.31.0.67\n') != -1:	# Found a Snort entry
# "TFTP Get" - interesting but not relevent to kojoney
    if line.find("ICMP PING ") != -1 or line.find("ICMP superscan ") != -1 or line.find("(portscan) ") != -1 :
        print "Snort entry is relevent to 172.31.0.67"
        fields=line.split(' ')
        print fields
        msg = " ".join(fields[6:])
        msg = msg.strip('\n');
        
        # Report
        print "log msg is : " + msg    
        makeMsg(0,"0","ids,RECON:" + msg)
        sendTweetSnort(msg)
        
# Process Netflows log entries
# Look for initial reconnaisance
#vi.e. NMAP pings etc
# TODO : add Nmap scan but only if dest is 172.31.0.67:22
# TODO : dump never seen before messages to a text file
def processFlows(line):
            
    #print "processFlows() : line read from Flows file : " + line + "\n"
    line=line.strip('\n')	# remove trailing \n
    
    # Parse Netflow
    # -------------    
    fields=line.split(" ")
    #print fields    
    
    a,srcIP = fields[0].split("=")
    
    a,srcPort = fields[1].split("=")
    
    a,dstIP = fields[2].split("=")
    #print "dstIP is " + dstIP
    
    a,dstPort = fields[3].split("=")
    #print "dstPort is " + dstPort
    
    a,proto = fields[4].split("=")
    #print "proto is " + proto
    
    a,bytes = fields[5].split("=")
    a,pkts  = fields[6].split("=")
    a,flags = fields[10].split("=")
    a,duration_msecs = fields[9].split("=")
    #print "duration_msecs is " + duration_msecs
    
    flow = srcIP + ":" + srcPort + "->" + dstIP + ":" + dstPort + " proto=" + proto + " flags=" + flags + " bytes=" + bytes + " pkts=" + pkts + " msecs=" + duration_msecs 
    print flow
    
    # Business Logic
    # --------------
    # Note that Tweet API uses port 80 so do not log that !
    # Case #1 : Extract SSH flows that are long enough not to be probes / SSH brute force attempts
    # SSH flow towards honeypot with duration >= 10 secs
    if dstIP == "172.31.0.67" and dstPort == "22" and int(duration_msecs) >= 10000:	
        makeMsg(0,"0","netflow,EXPL:Long-lived SSH session," + flow)
        sendTweetFlow("EXPL:Long-lived SSH session",flow)
    # Case #2 : Reconnaisance : ICMP towards honeypot
    elif dstIP == "172.31.0.67" and proto == "1" :	
        makeMsg(0,"0","netflow,RECON:ICMP," + flow)
        sendTweetFlow("RECON:ICMP",flow)
    # Case #3 : malware retrieval using port 80 (HTTP) from external IP but not to Tweet API web-server (NTT) or other web-services used by mars (tuwein sandbox) 
    elif srcIP == "172.31.0.67" and dstPort == "80" and dstIP.find("168.143.161.") == -1 and dstIP.find("168.143.162.") == -1 and dstIP.find("128.121.") == -1 and dstIP.find("128.130.") == -1 :
        makeMsg(0,"0","netflow,REINF:Malware retrieval?," + flow)
        sendTweetFlow("REINF:Malware retrieval?",flow)
    # Case #4 : malware retrieval using port 21 (FTP) from external IP
    elif srcIP == "172.31.0.67" and dstPort == "21" :
        makeMsg(0,"0","netflow,REINF:Malware retrieval?," + flow)
        sendTweetFlow("REINF:Malware retrieval?",flow)    
    else:
        pass
        #print "Netflow not interesting..."


def processSSH(line):
    global PreviousIPs
    global CLInum
    global SessionId
    global Username
    
    if Username == None:
        Username = "_unknown_"
            
    try:
        #print "line read from file\n:" + line
        
        # haxx0r guessed password OK
        # Use this one to perform the ipintellib() functions
        if line.find("authenticated with password") != -1:
            SessionId = SessionId + 1
            
            fields=line.split(',')
            #print fields
            a = fields[2].split()
            ip = a[0].rstrip(']')
            Username = a[1]
            #print "a is " + `a`
        
            # Get DNS info
            dnsInfo = ipintellib.ip2name(ip)
            dnsName = dnsInfo['name']
        
            # WHOIS information
            asInfo = ipintellib.ip2asn(ip)
            asNum = asInfo['as']				# AS123 
            asRegisteredCode = asInfo['registeredCode']		# Short-form e.g.ARCOR
        
            # GeoIP information
            geoIP = ipintellib.geo_ip(ip)
            countryCode = geoIP['countryCode']
            city        = geoIP['city']
            longitude   = geoIP['longitude']			# Used to calc approx. localtime
            
            msg = "------------------------------------------------------------------------------------------" 
            makeMsg(0,ip,msg)
            
            msg = "EXPL:authOK,"  + Username + "," + countryCode + "," + asNum + "," + asRegisteredCode + "," + city + "," + dnsName + ",long=" + "%.2f" % float(longitude)      
            makeMsg(0,ip,msg)
            
            # Write Security Visualisation Data to secViz file      
            print "Calling writeSecViz3()"
            writeSecViz3(ip,Username)
        
            # Compute localtime based on longitude
            locTime = calcLocalTime(longitude)
            msg = "INTEL:haxx0r localTime(est) is " + locTime      
            makeMsg(0,ip,msg)

            # Haxx0r's client stack information - using p0f 3.0.0, uptime is in seconds not hours
            try:
                p0fInfo = p0fcmd.getP0fInfo(ip,"0","172.31.0.67","22");
                if p0fInfo['result'] == True:		# p0f data is available
                    hops = p0fInfo['hops']
                    os   = p0fInfo['genre']
                    fw   = p0fInfo['firewall']
                    nat  = p0fInfo['nat']
                    if p0fInfo['genre'] == "Linux" :
                        uptime = p0fInfo['uptime']	# measured in secs 
                    else:
                        uptime = 0
                else:					# p0f data is not available
                    hops   = 0        
                    os     = "?"
                    fw     = "?"
                    nat    = "?"
                    uptime = 0
               
                #p0fStr = "os=" + os + " hops=" + hops + " lt=" + p0fInfo['linktype'] + " up=" + uptime + " tos=" + p0fInfo['tos'] + " masq=" + p0fInfo['masq'] + " fw=" + p0fInfo['firewall'] + " NAT=" + p0fInfo['nat'] + " realOS=" + p0fInfo['realos']
                p0fStr = "os=" + os + " hops=" + hops + " up=" + uptime + " fw=" + fw  + " NAT=" + nat 
                    
                # Compute haxx0r's PC bootTime based on p0f uptime (seconds)
                bootTime = calcBootTime(uptime)
                bootmsg = "haxx0r PC bootTime(est,UTC) is " + bootTime['timeStr']    

                # p0f info  
                msg = "p0f,INTEL:" + p0fStr	# INT = Intelligence      
                makeMsg(0,ip,msg)
                
                # haxx0r boot time 
                msg = "INTEL:bootTime," + bootmsg      
                makeMsg(0,ip,msg)
                
                # Has this IP been seen before ?
                if PreviousIPs.has_key(ip):			# IP has been seen before 
                    msg = "INTEL:IP was last seen " + PreviousIPs[ip]['lastVisitStr'] + " with a bootTime of " + PreviousIPs[ip]['timeStr']
                    makeMsg(0,ip,msg)
                    
                    # Has this PC stack been seen before ?
                    # i.e. are bootTimes within 30 minutes of each other ?
                    if abs(float(PreviousIPs[ip]['epoch']) - float(bootTime['epoch'])) < 1800.0:
                        msg = "INTEL:p0f uptime (secs) indicates repeat visit from haxx0r's PC from this ip"
                        makeMsg(0,ip,msg)
                else:
                    PreviousIPs[ip] = bootTime			# set info to be haxx0r boottime    
                    msg = "INTEL:first time visit from " + ip + ", user " + Username 
                    makeMsg(0,ip,msg)       
                     
            except Exception,e:
                syslog.syslog("Exception in processSSH() p0f for authOK section of code " + `e` + " ip=" + ip);
    
                
        # Extract haxxor's SSH client    
        elif line.find("pty request") != -1:
            fields=line.split(',')
            #print fields
            a = fields[2].split()
            #print "a is " + `a`
            ip = a[0].rstrip(']')
            pty = a[3]
            #print "pty is " + `pty`
            msg = "INTEL:client=" + pty 
            makeMsg(0,ip,msg)  
    
        # Disconnecting #1    
        elif line.find("sending close") != -1:
            fields=line.split(',')
            #print fields
            a = fields[2].split()
            ip = a[0].rstrip(']')
            #username = a[1]
            #print "a is " + `a`
            msg = "localClosed" 
            makeMsg(0,ip,msg) 
    
        # Disconnecting #2    
        elif line.find("remote close") != -1:
            fields=line.split(',')
            #print fields
            a = fields[2].split()
            ip = a[0].rstrip(']')
            #username = a[1]
            #print "a is " + `a`
            msg = "remoteClosed" 
            makeMsg(0,ip,msg) 
    
        # Request (OK or not OK) to download malware    
        elif line.find("Saved the file ") != -1:
            fields=line.split(',')
            print fields
            a = fields[2].split()
            ip = a[0].rstrip(']')
            fullFilename = a[4]
            fileName = os.path.basename(fullFilename)
        
            # GeoIP information
            geoIP = ipintellib.geo_ip(ip)
            countryCode = geoIP['countryCode']
        
            # Write Security Visualisation Data to secViz file      
            writeSecViz2(ip,Username,countryCode,fileName)
        
            makeMsg(0,ip,"REINF:haxxorDownloadRequest")            
            alertBody = "Requested filename :\n" + fileName
            #print "alertBody:\n" + alertBody 
   
            alert("Download requested",ip,Username,alertBody)
                      
        # haxx0r entered CLI command
        elif line.find("COMMAND IS") != -1:
            CLInum = CLInum + 1
        
            fields=line.split(',')
            # cliInfo = 
            a = fields[2].split()
            ip = a[0].rstrip(']')        
            #print "a is " + `a`
        
            cliInfo = a[4:]			# list containing CLI separated items - see backspaces
            cliInfoStr = " ".join(cliInfo)	# CLI as a single string
            
            # Write to log file       
            msg = "REINF:>>>," + cliInfoStr 
            makeMsg(CLInum,ip,msg) 
            
            # Send a Tweet
            sendTweetCLI(SessionId,Username,ip,cliInfoStr)
            
            if isHuman(cliInfo):
                makeMsg(CLInum,ip,"INTEL:humanHaxxor?")            
                alertBody = "haxx0r made a mistake typing the following :\n> " + cliInfoStr   
                alert("Human haxx0r online",ip,alertBody)
        
            # Write Security Visualisation Data to secViz file
            geoIP = ipintellib.geo_ip(ip)
            countryCode = geoIP['countryCode']      
            writeSecViz1(ip,Username,countryCode,cliInfoStr)
                                                 
    except Exception,e:
        syslog.syslog("kojoney_tail.py exception : processSSH() : " + `e` + " ip=" + ip)
    
# ----------------------------------------------
        
# Start of code        
        
       
# Make pidfile so we can be monitored by monit        
pid =  makePidFile("kojoney_tail")
if pid == None:
    syslog.syslog("Failed to create pidfile for pid " + `pid`)
    sys.exit(0)
else:
    syslog.syslog("kojoney_tail started with pid " + `pid`)
                
# Send an email to say kojoney_tail has started
makeMsg(0,"0","system,kojoney_tail started with pid=" + `pid`)
a = "kojoney_tail started with pid=" + `pid`

statusAlert("process started",a)

# Create a connection to Twitter
try:
    TweetClient = twitter.Api(username="honeytweeter",password="fuckfacebook")                
except Exception,e:
    syslog.syslog("kojoney_tail.py exception : main() : " + `e`)

# Set the Kojoney filename to scan
filename = '/var/log/kojoney.log'
file = open(filename,'r')

# Set the Snort filename to scan
filenameSnort = '/home/var/log/snort.syslog'
fileSnort = open(filenameSnort,'r')

# Set the Flows filename to scan
filenameFlows = '/home/var/log/gloworm-ermin.netflows'
fileFlows = open(filenameFlows,'r')

# Set the router syslog filename to scan
#filenameRouter = '/home/var/log/router.syslog'
#fileFlows = open(filenameFlows,'r')

# ------------
# tail -f mode
# ------------

# Find the size of the SSH file and move to the end
st_results = os.stat(filename)
st_size = st_results[6]
file.seek(st_size)

# Find the size of the Snort file and move to the end
st_results_snort = os.stat(filenameSnort)
st_size_snort = st_results_snort[6]
fileSnort.seek(st_size_snort)

# Find the size of the Flows file and move to the end
st_results_flows = os.stat(filenameFlows)
st_size_flows = st_results_flows[6]
fileFlows.seek(st_size_flows)

# add iptables, netflow to processed files
while 1:
    
    where = file.tell()
    line  = file.readline()
    
    whereSnort = fileSnort.tell()
    lineSnort  = fileSnort.readline()

    whereFlows = fileFlows.tell()
    lineFlows  = fileFlows.readline()
    
    # sleep if nothing to do
    # todo : syntax error here
    #if (not line) and if (not lineSnort) and if (not lineFlows) :
    #    print "sleeping..."
    #    time.sleep(1)
    
    if not line:		# no data in kojoney.log
        #print "nothing in Kojoney logfile to process"
        file.seek(where)
    else:			# new data has been added to log file
        #print "*** NEW EVENT in Kojoney logfile to process !"
        processSSH(line)
    
    if not lineSnort:		# no data in snort.syslog
        #print "nothing in Snort logfile to process"
        fileSnort.seek(whereSnort)
    else:			# new data has been added to log file
        #print "*** NEW EVENT in Snort syslog to process !"
        processSnort(lineSnort)
            
    if not lineFlows:		# no data in kojoney.log
        #print "nothing in Flows logfile to process"
        fileFlows.seek(whereFlows)
    else:			# new data has been added to log file
        #print "*** NEW EVENT in Flows logfile to process !"
        processFlows(lineFlows)
        
    #print "sleeping..."    
    time.sleep(1)
    
    


# ------------------
# batch process mode
# ------------------

#print "Run in batch mode"
#
#while True:
#    line = file.readline()
#    if not line : 
#        print "No data to read"
#        break
#    
#    process(line)
            
                                                                        