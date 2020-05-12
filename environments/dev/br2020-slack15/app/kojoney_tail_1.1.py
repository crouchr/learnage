#!/usr/bin/python

import time, os , syslog , urlparse 
import twitter		# Google API

import ipintellib	# RCH library - master on mars
import mailalert	# RCH library
import p0fcmd		# RCH library - master on mars
import rch_asn_funcs	# RCH library - master on mars

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
        asInfo = rch_asn_funcs.ip2asn(ip)
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
        print "notify     : e-mail : subject=" + '"' + alertSubject + '"'
        
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
        print "notify     : e-mail : subject=" + '"' + alertSubject + '"'  
        
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
        
        asInfo = rch_asn_funcs.ip2asn(ip)
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
    
        asInfo = rch_asn_funcs.ip2asn(ip)
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
        
        asInfo = rch_asn_funcs.ip2asn(ip)
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

# Candidate to replace secviz4 - uses source port from firewall and netflow logs to get accurate uptime
# Write Security Visualisation data to be processed by AfterGlow to .csv file
# This file is used for correlating haxx0r IP stack uptime with non-Kojoney events e.g. iptables and netflow events
# These events work because they have source port needed for accurate uptime calculation 
# Need to touch this file
# add hops ?
def writeSecViz4(ip,srcPort,dstIP,dstPort,event):

    #print "entered writeSecViz4()"
    now = time.time()
    
    try:    
        p0fInfo = p0fcmd.getP0fInfo(ip,srcPort,dstIP,dstPort);
        if p0fInfo['result'] == True :				# p0f data is available
            hops = p0fInfo['hops']
            os   = p0fInfo['genre']
            fw   = p0fInfo['firewall']
            nat  = p0fInfo['nat'] 
            if p0fInfo['uptime'] == "?":
                uptime = 0
            else :
                uptime = p0fInfo['uptime'] 
                
            #if p0fInfo['genre'] == "Linux" :
            #    uptime = p0fInfo['uptime'] 
            #    btes = now - int(uptime)
            #    hops = p0fInfo['hops']    
            #else:						# probably Windows
            #    uptimeHours = 0
            #    btes        = 0
            #    uptime      = 0
        else:							# p0f data not read OK
            hops   = 0        
            os     = "?"
            fw     = "?"
            nat    = "?"
            uptime = 0
                          
        # get current time
        timeTuple = time.localtime(now)
        nowStr    = time.asctime(timeTuple)			# current time
            
        # calc haxx0r bootTime based on seconds 	
        btes = now - int(uptime)
        timeTuple   = time.localtime(btes)
        bootTimeStr = time.asctime(timeTuple)
        bteh = int(btes/3600)
        #print "bootTimeEpochHours:" + `bteh`
        
        asInfo = rch_asn_funcs.ip2asn(ip)
        asNum = asInfo['as']					# AS123 
        asRegisteredCode = asInfo['registeredCode']		# Short-form e.g. ARCOR
        
        # old code from secviz3
        #msg = ip + "," + `bootTimeEpochHours` + "," + ip + ":" + Username + "," + "os=" + os + ",hops=" + hops + ","\
        #+ asRegisteredCode + ",now=" + nowStr + "," + `now` + ",bootTime=" + bootTimeStr + "," + `bte` + ",fw=" + fw + ",nat=" + nat
        
        # Add nowStr so that can see if the bteh/btes stays constant for multiple visits...
        # Log boottime epoch as bteh and btes to see how accurate they are
        # todo : add flow details 
        msg = ip + "," + `bteh` + "," + event + "," + os + "," + asNum + "(" + asRegisteredCode + ")" + ",now=" + nowStr + ",bootTime=" + bootTimeStr + ",btes=" + `btes` + ",uptime=" + `uptime`
        
        print "WriteSecViz4(): " + msg
        
        # file needs to be touched
        fpOut = open(r'/home/var/log/kojoney_tail_secviz4_uptime.csv','a')
        print >> fpOut,msg 
        fpOut.close()

    except Exception,e:
        syslog.syslog("kojoney_tail.py : writeSecViz4() exception caught = " + `e` + " ip=" + ip)


# Send a Tweet from  honeytweeter
# username is actually the global variable Username
def sendTweetCLI(sessionid,username,ip,cli):
        
    print "Entered sendTweetCLI()"
    
    now=time.time()
    
    try:
        # sessionid of -1 indicates that we have no AUTH_OK event and so no username - so don't tweet it
        if (int(sessionid) < 0):
            print "sessionId < 0 -> no previous AUTH_OK event to get username"
            return
        
        # This is flawed in that most p0f variables returned will be OK but uptime needs the source port specified   
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
        asInfo = rch_asn_funcs.ip2asn(ip)
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
        # todo - if os = windows, do not add bteh
        msg = "ssh:OTHER:sid=" + `sessionid` + ":IP=" + ip + ":" + asNum + "(" + asRegisteredCode + ")" + ":"\
        + countryCode + ":" + city + ":" + "%.2f" % longitude + ":" + os + ":" + hops\
        + ":fw=" + fw + ":nat=" + nat + ":bteh=" + `bteh`\
        + ": " + username + "@hpot $ " + cli

        # legacy Tweet code
        # Send the Tweet - max = 147 ?        
        #syslog.syslog("sendTweetCLI(): msg length=" + `len(msg)` + " chars")
        #print "Tweet=" + msg
        #
        # syslog every Tweet attempted to be sent    
        #syslog.syslog("sendTweetCLI(): " + msg)
        #
        #if len(msg) >= 140:
        #    msg=msg[0:140]
            
        sendTweet(msg)       
    
    except Exception,e:
        syslog.syslog("kojoney_tail.py : sendTweetCLI() exception caught = " + `e` + " ip=" + ip)

# wrapper for sending Tweets
def sendTweet(tweet_raw):
    global TweetClient
    
    MAXTWEET_LEN=139			# max chars to send
    
    now = time.time()
    
    try:
        # Anonymise and shorten actual honeypot IP address to HPOT
        tweet = tweet_raw.replace("172.31.0.67","HPOT")        
        
        # Construct and prepend a minimal localtime timestamp : HHMM   
        tuple=time.localtime(now)
        timestamp = "%02d" % tuple.tm_hour + "%02d" % tuple.tm_min    
        tweet = timestamp + ":" + tweet
    
        # Truncate (concatenate in future ?) long tweets 
        if len(tweet) >= MAXTWEET_LEN:
            tweet=tweet[0:MAXTWEET_LEN]
            tweet=tweet + "+"				# + indicates tweet was truncated
            syslog.syslog("kojoney_tail.py : sendTweet() [truncated to " + `len(tweet)` + " chars] : tweet=" + tweet)
        else:     
            syslog.syslog("kojoney_tail.py : sendTweet() [no truncation] : " + tweet)
        
        # actually send the tweet
        status = TweetClient.PostUpdate(tweet)    
        print "notify     : Tweet sent : " + tweet
        
        # log the Tweet - have a .txt extension so Windoze can open it up
        fpOut = open(r'/home/var/log/tweets.log.txt','a')
        print >> fpOut,"TWEET=" + tweet 
        fpOut.close()

        # send an e-mail if the exploit contains particularly interesting keywords
        if tweet.find("Cisco") != -1 or tweet.find("Conficker") != -1 or tweet.find("Downadup") != -1 :
            statusAlert("Exploit du jour detected",tweet)
        
        time.sleep(2)					# crude rate limit 
    
    except Exception,e:
        syslog.syslog("kojoney_tail.py : sendTweet() exception caught = " + `e` + " tweet=" + tweet)
        
# Send a Tweet from honeytweeter for interesting Snort events
def sendTweetSnort(event):
        
    #print "Entered sendTweetSnort()"
    
    try:
            
        # Construct Tweet
        msg = "ids:" + event
         
        sendTweet(msg)        
    
    except Exception,e:
        syslog.syslog("kojoney_tail.py : sendTweetSnort() exception caught = " + `e`)


# Send a Tweet from honeytweeter for interesting netflow events
def sendTweetFlow(event,flow):
        
    #print "Entered sendTweetFlow()"
    
    try:
            
        # Construct Tweet
        msg = "flw:" + event + ":" + flow
                
        sendTweet(msg)
        
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
    
    
# extract source IP from Snort log
# source IP can be either 1.2.3.4:80 or 1.2.3.4 (i.e. include a port number)
# make this a function and extend to extract srcip,srcport,dstIP,dstPort and return a dictionary

def getSrcIPSnort(line):
    sock={}
    try:
        #print "snort line is " + line
        a=line.find("}")
    
        if a == -1:	# Failed to find '}'
            return "0.0.0.0"
        
        b = line[a:].strip("\n")
    
        #print "b=" + b
        c=b[2:]			# skip "{ "
        #print "c=[" + c +"]"
    
        d = c.split(" ")		# d = 1.2.3.4 or 1.2.3.4:345
        #print "d is " + `d`
    
        if d[0].find(":") != -1 :	# d = 1.2.3.4:80
            sock['ip']  = d[0].split(":")[0]
            sock['port'] = d[0].split(":")[1]
        else:
            sock['ip']   = d[0]
            sock['port'] = -1
            
        #print "getSrcIPSnort() : ip is [" + sock['ip'] + "] and port is " + sock['port']
    
        return sock
    
    except Exception,e:
        syslog.syslog("kojoney_tail.py : getSrcIPSnort() exception caught = " + `e` + "line=" + line.strip("\n"))
        return None

# extract destination IP from Snort log
# IP can be either 1.2.3.4:80 or 1.2.3.4
# make this a function and extend to extract srcip,srcport,dstIP,dstPort and return a dictionary
def getDstIPSnort(line):
    sock={}
    
    try:
        #print "snort line is " + line
        a=line.find("}")
    
        if a == -1:	# Failed to find '}'
            return "0.0.0.0"
        
        b = line[a:].strip("\n")
    
        #print "b=" + b
        c=b[2:]			# skip "{ "
        #print "c=[" + c +"]"	# c = 1.2.3.4:80 -> 3.4.5.6:80
    
        d = c.split(" ")		# d = {'1.2.3.4', '->', '3.4.5.8'}
        #print "d is " + `d`
    
        if d[2].find(":") != -1 :	# d = 1.2.3.4:80
            sock['ip']   = d[2].split(":")[0]
            sock['port'] = d[2].split(":")[1]
        else:
            sock['ip']   = d[2]
            sock['port'] = -1
            
        #print "getDstIPSnort() : ip is [" + sock['ip'] + "] and port is " + sock['port']
    
        return sock
    
    except Exception,e:
        syslog.syslog("kojoney_tail.py : getDstIPSnort() exception caught = " + `e` + "line=" + line.strip("\n"))
        return None

# Process Snort log entries
# Look for initial reconnaisance
#vi.e. NMAP pings etc
# TODO : add Nmap scan but only if dest is 172.31.0.67:22
# TODO : dump never seen before messages to a text file
# todo : add writeSecViz4 for TCP-related events (i.e. can get an accurate uptime)
# create the phase from the snort message i.e look for EXPLOIT
def processSnort(line):
    try:        
        print "snort(ids) : " + line.strip('\n')
        
        # Extract the Snort event message
        fields=line.split(' ')
        #print fields
        snortMsg = " ".join(fields[6:])		# skip Snort timestamp
        snortMsg = snortMsg.strip('\n');
                     
        # Extract flow information from Snort message             
        srcSock = getSrcIPSnort(line)
        dstSock = getDstIPSnort(line)             
        flow = srcSock['ip'] + "(" + srcSock['port'] + ")" + "->" + dstSock['ip'] + "(" + dstSock['port'] + ")"               
                     
        # Tweet interesting IDS alerts 
        if line.find("ICMP PING ") != -1 or line.find("ICMP superscan ") != -1 or line.find("(portscan) ") != -1 :   
            msg = "RECON:" + flow + ": " + snortMsg + ":" + getIntelStr(srcSock['ip'],dstSock['ip']) 
            makeMsg(0,"0",msg)
            sendTweetSnort(msg)
        elif line.find("TFTP Get ") != -1 :
            msg = "REINF:" + flow + ": " + snortMsg + ":" + getIntelStr(srcSock['ip'],dstSock['ip']) 
            makeMsg(0,"0",msg)
            sendTweetSnort(msg)
        elif line.find("Potential SSH Scan ") != -1 :
            msg = "EXPLT:" + flow + ": " + snortMsg + ":" + getIntelStr(srcSock['ip'],dstSock['ip']) 
            makeMsg(0,"0",msg)
            # sendTweetSnort(msg) - too many to Tweet
        elif line.find("LibSSH Based ") != -1 :
            msg = "EXPLT:" + flow + ": " + snortMsg + ":" + getIntelStr(srcSock['ip'],dstSock['ip']) 
            makeMsg(0,"0",msg)
            # sendTweetSnort(msg) - too many to Tweet
        elif line.find("DNS SPOOF ") != -1 :
            msg = "EXPLT:" + flow + ": " + snortMsg + ":" + getIntelStr(srcSock['ip'],dstSock['ip']) 
            makeMsg(0,"0",msg)
            # sendTweetSnort(msg) - false positive - do not Tweet
        elif line.find("SQL Worm ") != -1 :
            msg = "EXPLT:" + flow + ": " + snortMsg + ":" + getIntelStr(srcSock['ip'],dstSock['ip']) 
            makeMsg(0,"0",msg)
            # sendTweetSnort(msg) - too many to Tweet
        else :
            if line.find(" EXPLOIT ") != -1 or line.find("Privilege") != -1 :		# attempt made to exploit the vulnerability
                msg = "EXPLT:" + flow + ": " + snortMsg + ":" + getIntelStr(srcSock['ip'],dstSock['ip'])
            elif line.find("ATTACK_RESPONSE") != -1 or line.find("ATTACK-RESPONSES") != -1 :	# host has been compromised 
                msg = "COMPR:" + flow + ": " + snortMsg + ":" + getIntelStr(srcSock['ip'],dstSock['ip'])
            else:
                msg = "OTHER:" + flow + ": " + snortMsg + ":" + getIntelStr(srcSock['ip'],dstSock['ip'])
            makeMsg(0,"0",msg)
            sendTweetSnort(msg)
            
    except Exception,e:
        syslog.syslog("kojoney_tail.py : processSnort() exception caught = " + `e` + "line=" + line)

# Add Snort alerts to a file to see of the (later) Netflow can be found for correlation
#def add2FlowWatchList(flow,event):
#    fpOut = open(r'/home/var/log/ids_flows.log','a')
#    print >> fpOut,flow + "," + event
#    fpOut.close()

# This is just alpha at the moment to check the file rollover logic
# todo : extract the destination IP and perform ipintel functions on it
def processAmunDownload(line):
    try:        
        print "amun_dload : " + line.strip('\n')
  
        if line.find("ftp connect to") != -1 or line.find("TFTP Request") != -1:            
            msg = "amun:REINF:" + line.strip('\n')    
            makeMsg(0,"0",msg)
            sendTweet(msg) 
        elif line.find("[ftp_download]") !=-1:		# log all the FTP session, but no Tweet
            msg = "amun:REINF:" + line.strip('\n')    
            makeMsg(0,"0",msg)        
        #else :
        #    syslog.syslog("processAmunDownload(): " + line)	# log the entry    
            
    except Exception,e:
        syslog.syslog("kojoney_tail.py : processAmunDownload() exception caught = " + `e` + "line=" + line)


# Look for src port for data to Kojoney so that p0f can be accurate
# this is restricted to SSH at the moment - should it be extended in order to get more uptimes ?
# todo : Make this a stand-alone funtion for parsing iptables 
def processFW(line):
    
    try:        
        #print "processFW() : line read from iptables file : " + line.strip('\n')
        
        #if line.find("DST=172.31.0.67") != -1 and line.find("DPT=22") != -1 :
        
        a = line.find("SRC=")		# source IP
        b = line.find("SPT=")		# source port
        c = line.find("DST=")		# destination IP
        d = line.find("DPT=")		# dest port
        e = line.find("PROTO=")		# TCP UDP
        f = line.find("TTL=")		# TTL for OS fingerprinting compared to p0f
        g = line.find("ID=")		# IP ID
    
        srcIP   = line[a:].split(" ")[0].split("=")[1]
        srcPort = line[b:].split(" ")[0].split("=")[1]
        dstIP   = line[c:].split(" ")[0].split("=")[1]    
        dstPort = line[d:].split(" ")[0].split("=")[1]    
        proto   = line[e:].split(" ")[0].split("=")[1]
        ttl     = line[f:].split(" ")[0].split("=")[1]
        ipid    = line[g:].split(" ")[0].split("=")[1]
    
        flow1 = srcIP + "(" + srcPort + ")" + "->" + dstIP + "(" + dstPort + ")" + " proto=" + proto
        flow2 = " ttl=" + ttl + " ipid=" + ipid 
        #print "iptables   : " + flow1 + ":" + flow2
        
        if (dstPort == "43" or srcPort == "43" or srcPort == "4321" or dstPort == "4321") :	# ignore WHOIS
            return
            
        #if (dstPort != "43" and srcPort != "43" and srcPort != "4321" and dstPort != "4321") :	# what is 4321 ?
        event = "iptables:MISC:" + flow1 + ":" + getIntelStr(srcIP,dstIP) + ":" + flow2
        print "iptables   : " + event
        # Log to kojoney_tail.log    
        makeMsg(0,"0",event)
    
        # Anomaly : Low TTL
        if int(ttl) < 25:
            event = "iptables:ANOMALY:TTL<25:" + flow1 + ":" + getIntelStr(srcIP,dstIP) + ":" + flow2
            print "iptables   : " + event
            makeMsg(0,"0",event)
         
        # todo : crude OS fingerprinting ?
    
        # secViz : Log uptime if this is a TCP session towards the honeypot
        if proto == 'TCP' and dstIP == "172.31.0.67" :
            writeSecViz4(srcIP,srcPort,dstIP,dstPort,event)
        
        # too large and too frequent a message to Tweet without truncation / filtering
    
    except Exception,e:
        syslog.syslog("kojoney_tail.py : processFW() exception caught = " + `e` + "line=" + line)

# Process p0f log
# todo : extract src IP and preform getInteStr() on it
def processp0f(line):
    
    pass
    return
    
    try:        
        
        print "p0f        : " + line[27:].strip('\n')	# skip the date portion
        event = "INTEL:p0f:"  + line[27:].strip('\n')
        
        # Log to kojoney_tail.log - remove if too much info + do not Tweet     
        makeMsg(0,"0",event)
    
    except Exception,e:
        syslog.syslog("kojoney_tail.py : processp0f() exception caught = " + `e` + "line=" + line)

# Process Apache error log 
# todo : extract src IP and preform getInteStr() on it
# initial version just copies error event to Kojoney_tail.py
def processWeb(line):
    
    try:            
        print "web        : " + line.strip('\n')	
        
        # only log errors and not debug,notice and info messages
        if line.find("[error]") != -1:
            event = "MISC:web:"  +  line.strip('\n')
            # Log to kojoney_tail.log - remove if too much info + do not Tweet     
            makeMsg(0,"0",event)
    
    except Exception,e:
        syslog.syslog("kojoney_tail.py : processWeb() exception caught = " + `e` + "line=" + line)

        
# Process Netflows log entries
# Look for initial reconnaisance
#vi.e. NMAP pings etc
# TODO : add Nmap scan but only if dest is 172.31.0.67:22
# TODO : dump never seen before messages to a text file
def processFlows(line):
    
    try:            
        #print "processFlows() : line read from Flows file : " + line + "\n"
        line=line.strip('\n')	# remove trailing \n
    
        # Parse Netflow
        # -------------    
        fields=line.split(" ")
        #print fields    
    
        a,rtr = fields[0].split("=")
    
        a,srcIP = fields[1].split("=")
    
        a,srcPort = fields[2].split("=")
    
        a,dstIP = fields[3].split("=")
        #print "dstIP is " + dstIP
    
        a,dstPort = fields[4].split("=")
        #print "dstPort is " + dstPort
    
        a,proto = fields[5].split("=")
        #print "proto is " + proto
    
        a,bytes = fields[6].split("=")
        a,pkts  = fields[7].split("=")
        avg = int(bytes)/int(pkts)		# Average packet size
        
        a,inIf   = fields[8].split("=")
        a,outIf  = fields[9].split("=")
        
        a,flags = fields[13].split("=")
        a,duration_msecs = fields[12].split("=")
        
        if proto == "6" :	# TCP
            flow = rtr + ":" + srcIP + "(" + srcPort + ")" + "->" + dstIP + "(" + dstPort + ")" + " B=" + bytes + " D=" + duration_msecs + " P=" + pkts + " pr=" + proto + " AVG=" + `avg` + " F=" + flags
        else : 			# flags are not relevant
            flow = rtr + ":" + srcIP + "(" + srcPort + ")" + "->" + dstIP + "(" + dstPort + ")" + " B=" + bytes + " D=" + duration_msecs + " P=" + pkts + " pr=" + proto + " AVG=" + `avg` 
        
        # Ignore all flows to/from the local LAN
        if srcIP.find("192.168.1.") != -1 or dstIP.find("192.168.1.") != -1 :
            #print "Local LAN traffic -> ignore : " + flow
            return
            
        if (srcPort == "43" or dstPort == "43" or dstPort == "4321" or dstPort == "4321") :	# bug - this is Whois port
            #print "netflow    : ignoring WHOIS query " + flow
            return
        elif (srcIP == "172.31.0.67" and dstPort == "80" and proto == "6" and (dstIP.find("168.143.161.") != -1 or dstIP.find("168.143.162.") != -1 or dstIP.find("128.121.") != -1 or dstIP.find("128.130.") != -1)) :
            #print "netflow    : ignoring Twitter / Sandbox APIs " + flow
            return
        elif srcIP == "172.31.0.67" and dstPort == "25" and proto == "6" :
            print "netflow    : ignoring SMTP session " + flow
            return
        else:
            print "netflow    : " + flow + ":" + getIntelStr(srcIP,dstIP)	
    
        # Business Logic - anomalous behaviour
        # --------------
        # Note that Tweet API uses port 80 so do not log that !
        
        # Case #1 : Extract SSH flows that are long enough not to be probes / SSH brute force attempts
        # SSH flow towards honeypot with duration > 30 secs
        if (dstIP == "172.31.0.67" and dstPort == "22" and int(duration_msecs) > 30000 and proto == "6") :	
            msg = "EXPLT:SSH>30s:" + getIntelStr(srcIP,dstIP)
            makeMsg(0,"0",msg)		# bug msg does not have the flow in it !
            sendTweetFlow(msg,flow)
            writeSecViz4(srcIP,srcPort,"172.31.0.67","22","EXPL:flw:SSH_session")
        # Case #2 : Reconnaisance : ICMP towards honeypot
        # todo : unreachables ?
        elif (dstIP == "172.31.0.67" and proto == "1") :	
            msg = "RECON:ICMP:" + getIntelStr(srcIP,dstIP)
            makeMsg(0,"0",msg)
            sendTweetFlow(msg,flow)
        # Case #2 : Do not Tweet short SSH sessions - i.e. the brute force attempts
        elif (dstIP == "172.31.0.67" and dstPort == "22") :	
            msg = "RECON/BRUTE:SSH:" + getIntelStr(srcIP,dstIP)
            makeMsg(0,"0",msg)
            return
            #sendTweetFlow(msg,flow)    
        # Case #4 : Malware retrieval using port 80 (HTTP) from external IP 
        elif (srcIP == "172.31.0.67" and dstPort == "80" and proto == "6") :
            msg = "REINF:HTTP_xfer:" + getIntelStr(srcIP,dstIP)
            makeMsg(0,"0",msg)
            sendTweetFlow(msg,flow)
        # Case #5 : Malware retrieval using port 21 (FTP) from external IP
        elif (srcIP == "172.31.0.67" and dstPort == "21" and proto == "6") :
            msg = "REINF:FTP_xfer:" + getIntelStr(srcIP,dstIP)
            makeMsg(0,"0",msg)
            sendTweetFlow(msg,flow)
        # Case #6 : Malware retrieval using port 69 (TFTP) from external IP
        elif (srcIP == "172.31.0.67" and dstPort == "69" and proto == "17") :
            msg = "REINF:TFTP_xfer:" + getIntelStr(srcIP,dstIP)
            makeMsg(0,"0",msg)
            sendTweetFlow(msg,flow)
        # Case #7 : NetBIOS long-lived sessions - anything longer than 10 seconds (but ignore e-mail alerts)
        elif (srcIP == "172.31.0.67" and int(duration_msecs) > 20000 and (srcPort == "135" or srcPort == "445")) :
            msg = "SUSPC:NetBIOS_Dur>20s:" + getIntelStr(srcIP,dstIP)
            makeMsg(0,"0",msg)
            sendTweetFlow(msg,flow)    
        # Case #8 : NetBIOS large amount of data transferred - anything more than 1 Kbytes
        elif (srcIP == "172.31.0.67" and int(bytes) > 4096 and (srcPort == "135" or srcPort == "445")) :
            msg = "SUSPC:NetBIOS_TX>4KB:" + getIntelStr(srcIP,dstIP)
            makeMsg(0,"0",msg)
            sendTweetFlow(msg,flow)     
        # Case #9 : Generic long-lived sessions - anything longer than 10 seconds (but ignore e-mail alerts)
        elif (srcIP == "172.31.0.67" and int(duration_msecs) > 20000 and dstPort != "25") :
            msg = "SUSPC:Dur>20s:" + getIntelStr(srcIP,dstIP)
            makeMsg(0,"0",msg)
            sendTweetFlow(msg,flow)    
        # Case #10 : Generic large amount of data transferred - anything more than 5 Kbytes
        elif (srcIP == "172.31.0.67" and int(bytes) > 4096 and dstPort != "25") :
            msg = "SUSPC:TX>4KB:" + getIntelStr(srcIP,dstIP)
            makeMsg(0,"0",msg)
            sendTweetFlow(msg,flow)        
        else:
            pass
            #print "Netflow not interesting..."
    
    except Exception,e:
        syslog.syslog("kojoney_tail.py : processFlows() exception caught = " + `e` + "line=" + line)

# add try: exception to this
# get intel on not the hpot IP 
def getIntelStr(ip1,ip2):
    
    #print "Called getIntelStr(): ip=" + ip
    
    ip = "0.0.0.0"
    
    try: 
        if ip1 == "172.31.0.67" :
            ip = ip2
        if ip2 == "172.31.0.67" :
            ip = ip1    
        
        #if ip == "0.0.0.0" :		# failed to extract IP from a record
        #    return "intell=0.0.0.0"
    
        # Get DNS info
        dnsInfo = ipintellib.ip2name(ip)
        dnsName = dnsInfo['name']
        
        # WHOIS : primary information
        asInfo = rch_asn_funcs.ip2asn(ip)
        asNum = asInfo['as']					# AS123 
        asRegisteredCode = asInfo['registeredCode']		# Short-form e.g.ARCOR
        countryCode = asInfo['countryCode']
        
        # WHOIS info gathered from "infos" fields
        info        = asInfo['info']
        purpose     = asInfo['purpose']
        vodafone    = asInfo['vodafone']
        
        # GeoIP information
        #geoIP = ipintellib.geo_ip(ip)				# getting exceptions still !
        #countryCode = geoIP['countryCode']
        #city        = geoIP['city']
        #longitude   = geoIP['longitude']			# Used to calc approx. localtime
    
        #intelStr = countryCode + ":" + asNum + ":" + asRegisteredCode + ":" + city + ":" + dnsName 
        intelStr = countryCode + ":" + asNum + ":" + asRegisteredCode + ":" + dnsName + ":info=" + info + ":purpose=" + purpose + ":vodafone:" + vodafone   
    
        # ,long=" + "%.2f" % float(longitude) 
        #print "intelStr is " + intelStr
         
        return intelStr        

    except Exception,e:
        syslog.syslog("kojoney_tail.py : getIntelStr() exception caught = " + `e` + "ip=" + ip)
        return "intell=exception!"

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
            asInfo = rch_asn_funcs.ip2asn(ip)
            asNum = asInfo['as']				# AS123 
            asRegisteredCode = asInfo['registeredCode']		# Short-form e.g.ARCOR
        
            # GeoIP information
            geoIP = ipintellib.geo_ip(ip)
            countryCode = geoIP['countryCode']
            city        = geoIP['city']
            longitude   = geoIP['longitude']			# Used to calc approx. localtime
            
            msg = "------------------------------------------------------------------------------------------" 
            makeMsg(0,ip,msg)
            
            msg = "EXPLT:authOK,"  + Username + "," + countryCode + "," + asNum + "," + asRegisteredCode + "," + city + "," + dnsName + ",long=" + "%.2f" % float(longitude)      
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
                msg = "INTEL:" + p0fStr	# INT = Intelligence      
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
            
            # E-mail that the haxxor has downloaded a file        
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
    
def genAmunSuffix():
    now = time.time()
    tuple = time.localtime(now)
    #filepath = "/usr/local/src/amun/logs/" + filename + "." + `tuple.tm_year` + "-" + "%02d" % tuple.tm_mon + "-" + "%02d" % tuple.tm_mday
    suffix = `tuple.tm_year` + "-" + "%02d" % tuple.tm_mon + "-" + "%02d" % tuple.tm_mday
    
    return suffix
       
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
    syslog.syslog("kojoney_tail.py exception connecting to Twitter : main() : " + `e`)
    
# Set the Kojoney filename to scan
filename = '/var/log/kojoney.log'
file = open(filename,'r')

# Set the Snort filename to scan
filenameSnort = '/home/var/log/snort.syslog'
fileSnort = open(filenameSnort,'r')

# Set the fprobe Flows filename to scan
filenameFlows = '/home/var/log/gloworm-ermin.mars_fp.netflows'
fileFlows = open(filenameFlows,'r')

# Set the Border Gateway Flows filename to scan
filenameBGFlows = '/home/var/log/gloworm-ermin.bg_rtr.netflows'
fileBGFlows = open(filenameBGFlows,'r')

# Set the iptables filename to scan
filenameFW = '/home/var/log/iptables.syslog'
fileFW = open(filenameFW,'r')

# Set the p0f filename to scan
filenamep0f = '/home/var/log/p0f.log'
filep0f     = open(filenamep0f,'r')

# Set the Apache filename to scan
filenameWeb = '/var/log/httpd/error_log'
fileWeb     = open(filenameWeb,'r')

# Set the Amun Download filename to scan
Today = genAmunSuffix()
filenameAmunDownload = '/usr/local/src/amun/logs/download.log'
fileAmunDownload = open(filenameAmunDownload,'r')

# Set the Amun Submissions filename to scan
filenameAmunSubmit = '/usr/local/src/amun/logs/submissions.log'
fileAmunSubmit = open(filenameAmunSubmit,'r')

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

# Find the size of the honeypot fprobe netflows file and move to the end
st_results_flows = os.stat(filenameFlows)
st_size_flows = st_results_flows[6]
fileFlows.seek(st_size_flows)

# Find the size of the Border Gateway router netflows file and move to the end
st_results_bgflows = os.stat(filenameBGFlows)
st_size_bgflows = st_results_bgflows[6]
fileBGFlows.seek(st_size_bgflows)

# Find the size of the iptables file and move to the end
st_results_fw = os.stat(filenameFW)
st_size_fw = st_results_fw[6]
fileFW.seek(st_size_fw)

# Find the size of the p0f file and move to the end
st_results_p0f = os.stat(filenamep0f)
st_size_p0f = st_results_p0f[6]
filep0f.seek(st_size_p0f)

# Find the size of the Web-server file and move to the end
st_results_Web = os.stat(filenameWeb)
st_size_Web = st_results_Web[6]
fileWeb.seek(st_size_Web)

# Find the size of the Amun Download file and move to the end
st_results_amunDownload = os.stat(filenameAmunDownload)
st_size_amunDownload = st_results_amunDownload[6]
fileAmunDownload.seek(st_size_amunDownload)

# Find the size of the Amun Submissions file and move to the end
st_results_amunSubmit = os.stat(filenameAmunSubmit)
st_size_amunSubmit = st_results_amunSubmit[6]
fileAmunSubmit.seek(st_size_amunSubmit)

while True:

    today = genAmunSuffix()
    if today != Today:		# Amun log file midnight rollover ?
        syslog.syslog("kojoney_tail.py : Amun logfile rolled over, re-open the file");
        time.sleep(120)		# Wait two minutes
        Today = today
        
        # Amun Download log file
        fileAmunDownload.close()
        fileAmunDownload = open(filenameAmunDownload,'r')
        st_results_amunDownload = os.stat(filenameAmunDownload)
        st_size_amunDownload = st_results_amunDownload[6]
        fileAmunDownload.seek(st_size_amunDownload)
        
        # Amun Submissions log file
        fileAmunSubmit.close()
        fileAmunSubmit = open(filenameAmunSubmit,'r')
        st_results_amunSubmit = os.stat(filenameAmunSubmit)
        st_size_amunSubmit = st_results_amunSubmit[6]
        fileAmunSubmit.seek(st_size_amunSubmit)
    
    # Kojoney        
    where = file.tell()
    line  = file.readline()
    
    # Snort
    whereSnort = fileSnort.tell()
    lineSnort  = fileSnort.readline()
    
    # Honeypot fprobe netflows
    whereFlows = fileFlows.tell()
    lineFlows  = fileFlows.readline()
    
    # Border Router netflows
    whereBGFlows = fileBGFlows.tell()
    lineBGFlows  = fileBGFlows.readline()
    
    # iptables
    whereFW = fileFW.tell()
    lineFW  = fileFW.readline()
    
    # p0f
    wherep0f = filep0f.tell()
    linep0f  = filep0f.readline()
    
    # Web-server
    whereWeb = fileWeb.tell()
    lineWeb  = fileWeb.readline()
    
    # Amun download.log
    whereAmunDownload = fileAmunDownload.tell()
    lineAmunDownload  = fileAmunDownload.readline()
    
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
            
    if not lineFlows:		# no data in fprobe netflows log file
        #print "nothing in honeypot fprobe logfile to process"
        fileFlows.seek(whereFlows)
    else:			# new data has been added to log file
        #print "*** NEW EVENT in Flows logfile to process !"
        processFlows(lineFlows)
    
    if not lineBGFlows:		# no data in Border Gateway netflows log file
        #print "nothing in Border Gateway router netflow logfile to process"
        fileBGFlows.seek(whereBGFlows)
    else:			# new data has been added to log file
        #print "*** NEW EVENT in Border Gateway router netflow logfile to process !"
        processFlows(lineBGFlows)
    
    if not lineFW:		# no data in kojoney.log
        #print "nothing in iptables syslog file to process"
        fileFW.seek(whereFW)
    else:			# new data has been added to log file
        #print "*** NEW EVENT in iptables syslog file to process !"
        processFW(lineFW)
    
    if not linep0f:		# no data in p0f.log
        #print "nothing in p0f log file to process"
        filep0f.seek(wherep0f)
    else:			# new data has been added to log file
        #print "*** NEW EVENT in p0f log file to process !"
        processp0f(linep0f)
    
    if not lineWeb:		# no data in Apache error log
        #print "nothing in Apache error log file to process"
        fileWeb.seek(whereWeb)
    else:			# new data has been added to log file
        #print "*** NEW EVENT in Apache error log file to process !"
        processWeb(lineWeb)
    
    if not lineAmunDownload:		# no data in Amun download.log
        #print "nothing in Amu download.log file to process"
        fileAmunDownload.seek(whereAmunDownload)
    else:			# new data has been added to log file
        #print "*** NEW EVENT in iptables syslog file to process !"
        processAmunDownload(lineAmunDownload)
    
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
            
                                                                        