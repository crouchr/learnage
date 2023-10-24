#!/usr/bin/python

# Tail the Kojoney Channel and send out Tweets

import time, os , syslog , re 
import twitter		# Google API
from urlparse import urlparse

import ipintellib	# RCH library - master on mars
import mailalert	# RCH library
import p0fcmd		# RCH library - master on mars
import filter_sebek     # RCH library - master on mars
import extract_url      # RCH library - master on mars

#import rch_asn_funcs	# RCH library - master on mars

#import getSnortInfo	# RCH code - not a module

# Globals
#PreviousIPs = {}
#CLInum=0		# number of lines of CLI processed
#Version="1.2"		# added p0f v 3.0.0
#TweetVersion="0.2"	# update if Tweet format changes
#SessionId=-1		# incremented for every authenticated (authOK) session
#Username = "_unknown_"	# Uninitialised

ROUTER = "172.31.0.9"
HPOT   = "172.31.0.67"
HONEYD = "172.31.0.1"

IBG    = "172.31.0.47"	# IP address sending netflow 

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


def statusAlert(subject,content):
    smtpServer   = 'smtp.btconnect.com'
    sender       = 'the.crouches@btconnect.com'
    destination  = ['richard.crouch@vodafone.com']
    debugLevel   = False
    
    try:
        
        now = time.time()
        nowLocal = time.gmtime(now)

        # Notify !
        alertSubject = "honeypot status : " + subject
        alertContent = content + "\n\nSent by Kojoney Honeypot on " + time.asctime(nowLocal) + "\n\n"                 
        
        #print "alert subject:" + alertSubject + "\nalertContent:\n" + content + "\n"
        
        status = mailalert.mailalert(sender,destination,smtpServer,alertSubject,alertContent,debugLevel)        
        
        # uncomment the following line if you want to see the e-mail being sent
        print "notify     : e-mail : subject=" + '"' + alertSubject + '"'  
        
        # Add a record to syslog
        a = "Sent alert e-mail, Subject=" + alertSubject + " to " + destination[0]
        syslog.syslog(a)
    
    except Exception,e:
        syslog.syslog("kojoney_tweet.py : statusAlert() : " + `e`)

# process kojoney_tail.log
# this is too vebose - need to re-think this 
def processChannelTweet(line):
    #print "entered processChannelTweet()"

    try:
        fields=line.split(",")
        print "processChannelTweet() : " + `fields`
        
        timeS       = fields[0]
        type        = fields[4]		# e.g. ids , flow , amun , aaa , honeyd
        node        = fields[5]		# e.g. mars
        phase       = fields[6]		# 
                
        # Filter
        # Ignore Amun events - no IP address
        #if type.find("amun") != -1 :		
        #    return
        
        # Ignore AAA events - no IP address
        #if type.find("aaa") != -1 :		
        #    return
        
        # Extract event independent fields
        srcIP       = fields[14]
        dstIP       = fields[18]
        event       = fields[21]	# The last mandatory field
        eventInfo   = fields[22]
        
        # Additional info not used by Afterglow but added to output file
        countryCode = fields[7]
        ASname      = fields[8]
        AScode      = fields[9]
        city        = fields[10]
        lat         = fields[11]
        long        = fields[12]
        dstPort     = fields[19]
        proto       = fields[17]
        dnsName     = fields[11]
        
        # Strip () from destination port
        dstPort = dstPort.lstrip('(')
        dstPort = dstPort.rstrip(')')
        
        # Replace proto with single character if one of TCP,UDP,ICMP
        if proto == '[6]' :
            proto = 'T'
        if proto == '[1]' :    
            proto = 'I'
        if proto == '[17]' :
            proto = 'U'    
        if proto.find('[T]') != -1 :
            proto = 'T' 
        if proto.find('[U]') != -1 :
            proto = 'U'
        if proto.find('[I]') != -1 :
            proto = 'I:'	# add a separator character 
        
        # Compress Phase
        if phase.find("FLOOD") != -1 :
            phase = "FLD" 
        if phase.find("RECON") != -1 :
            phase = "REC" 
        if phase.find("SUSPC") != -1 :
            phase = "SUS" 
        if phase.find("OTHER") != -1 :
            phase = "-" 
        if phase.find("REINF") != -1 :
            phase = "REI" 
        
        # Compress Type
        if type.find("ids") != -1 :
            type = "IDS"
        if type.find("ips") != -1 :
            type = "IPS" 
        if type.find("flow") != -1 :
            type = "FL" 
        if type.find("web") != -1 :
            type = "WW" 
        if type.find("adsl") != -1 :
            type = "FW" 
        if type.find("Aaa") != -1 :
            type = "AAU"
        if type.find("aaA") != -1 :
            type = "AAC" 
        if type.find("amun") != -1 :
            type = "AM" 
        if type.find("acl") != -1 :
            type = "ACL" 

        # Add countryCode to any non-honeypot IPs
        srcIPinfo = srcIP
        dstIPinfo = dstIP
        if srcIP != "HPOT":
            srcIPinfo = srcIP + ":" + countryCode
        if dstIP != "HPOT":
            dstIPinfo = dstIP + ":" + countryCode
            
                    
        # For flow-derived events, construct the secviz file output fields[0-2] + additional info     
        #addInfo = ",time=" + timeS + ",ASname=" + ASname + ",CC=" + countryCode + ",event=" + event + ",dns=" + dnsName + ",AScode=" + AScode
        msg = type + "," + node + "," + phase + "," + countryCode + "," + ASname + "," + AScode + "," + srcIP + "->" + dstIP + "(" + dstPort + ")" + "," + event + "," + eventInfo + "," + dnsName 
        
        # Do not visualise return flows - this needs to be done using proper correlation in next version
        # Needs more thought
        #if int(dstPort) < 1024 and srcIP == "HPOT" :
        #    syslog.syslog("writeSecviz5() discarded return flow : " + msg)  
        
        # Compress node (sources of event)
        msg=msg.replace("bg_rtr"  ,"BG")		# BG Router
        msg=msg.replace("node9"   ,"HR")		# Honeypot Router
        msg=msg.replace("mars_fp" ,"HP")		# Honeypot
        msg=msg.replace("mars"    ,"HP")		# Honeypot - fwsnort
        msg=msg.replace("adsl"    ,"FW")		# WRT ADSL router
        
        # Misc compression
        #msg=msg.replace("FEED:netflow","")
        #msg=msg.replace("FEED:iptables","")
        #msg=msg.replace("cli:router:","")
        #msg=msg.replace('T22/23',"")
        #msg=msg.replace("ACL:router:EVENT:","")
        
        #msg=msg.replace("p0f:H:FEED:OS=","")
        #msg=msg.replace("WW:H:FEED:File does not exist: ","")

        #print "tweet before compression=" + msg
        
        sendTweet(msg)
        
        # file needs to be touched
        fpOut = open(r'/home/var/log/kojoney_tail_tweets.csv','a')
        #secviz5_tweets.csv','a')
        print >> fpOut,msg 
        fpOut.close()

    except Exception,e:
        syslog.syslog("kojoney_tweet.py : processChannelTweet() exception caught = " + `e` + " line=" + line)


# /var/log/messages   
#May 10 06:48:30 mars sshd[1122]: Accepted password for test from 172.31.0.68 port 1028 ssh2 
#May 10 08:52:50 mars sshd[1291]: Failed password for test from 172.31.0.68 port 1029 ssh2 
#May 10 08:52:52 mars sshd[1291]: Accepted password for test from 172.31.0.68 port 1029 ssh2 
#May 10 14:26:15 mars sshd[9525]: Accepted password for crouchr from 192.168.1.248 port 49918 ssh2
def processMessages(line):

    try :
        line=line.strip("\n")
        #print "processMessages() : line read from /var/log/messages : " + line
                    
        if line.find("from 192.168.1.") != -1 :         # do not log legitimate local LAN access 
            return
            
        if line.find("mars sshd") == -1 :
            return
        if line.find("Accepted password for") == -1 :
            return
        
        print "processMessages() : candidate line read from /var/log/messages : " + line
                                                                                 
        # Parse
        # -----    
        pat = r'\d+\.\d+\.\d+\.\d+'             # locate a number of IP addresses
        ips = re.findall(pat,line)     
                                                                                                                 
        #fields=line.split(" ")
        #print fields                            # locate username
        #username = fields[9]    
        pat = r'password for (\w+)'             # locate a number of IP addresses
        username = re.findall(pat,line)[0]     
        print "kojoney_tweet.py : processMessages() : username is " + username
        
                                                                                                                                         
        srcIP   = ips[0]
        #dstIP   = "HPOT"
        dstIP   = "172.31.0.67"
        dstPort = "22"
        proto   = "6"                                                   # Tevent   = "user=" + username                                    # todo : parse the user     
                                                                                                                                                                                         
        # Get OS type of SRC IP    
        
        print "kojoney_tweet.py : processMessages() : p0f input is srcIP=" + srcIP + " dstIP=" + dstIP + " dstPort=" + dstPort
        
        p0fInfo = p0fcmd.getP0fInfo(srcIP,"0",dstIP,dstPort);           # 0 = wildcard the srcPort
        if p0fInfo['result'] == True :                                  # p0f data is available   
            os   = p0fInfo['genre']
            nat  = p0fInfo['nat'][0]
            hops = p0fInfo['hops']
        else:
            os   = "?"
            nat  = "?"
            hops = "?"
        
        # Get DNS info
        dnsInfo = ipintellib.ip2name(srcIP)
        dnsName = dnsInfo['name'].rstrip('.')                   # right-strip the trailing .
        
        # WHOIS         
        asInfo = ipintellib.ip2asn(srcIP)                               # 
        asNum = asInfo['as']		                                # AS123   
        asRegisteredCode = asInfo['registeredCode']                     # Short-form e.g.ARCOR
 
        # GeoIP information - faster than WHOIS for looking up Country Code information
        geoIP = ipintellib.geo_ip(srcIP)                                
        countryCode = geoIP['countryCode']                              
        city        = geoIP['city']
        longitude   = geoIP['longitude']                                # Used to calc approx. localtime
        latitude    = geoIP['latitude']    

        msg  = "INTRUSION" + \
                ",user="  + username + \
                ",IP="    + srcIP +  \
                ",p0f="   + os + " NAT=" + nat + " hops=" + hops + \
                ",DNS="   + dnsName +  \
                ",WHOIS=" + asNum + " (" + asRegisteredCode + ")" + \
                ",GeoIP=" + countryCode + " " + city + " " + "%.2f" % longitude + "E"
                
        print "tweet before compression : " + msg
        sendTweet(msg)
    
    except Exception,e:
        syslog.syslog("kojoney_tweet.py : processMessages() exception caught = " + `e` + " line=" + line)


#Jun 15 10:15:09 mars passwd[28828]: password for `test' changed by `test' 
#Jun 19 10:38:23 mars passwd[1155]: password for `admin' changed by `admin' 
#Jun 19 10:43:40 mars passwd[1509]: password for `test' changed by `test' 
#Jun 23 00:05:16 mars passwd[32394]: password for `apache' changed by `apache' 
def processSecure(line):

    try :
        line=line.strip("\n")
        #print "processSecure() : line read from /var/log/secure : " + line
                    
        #if line.find("from 192.168.1.") != -1 :         # do not log legitimate local LAN access 
        #    return
            
        if line.find("mars passwd") == -1 :
            return
            
        if line.find(" password for ") == -1 :
            return
        print "processSecure() : candidate line read from /var/log/secure : " + line
                                                                                 
        # Parse
        # -----    
        #pat = r'\d+\.\d+\.\d+\.\d+'             # locate a number of IP addresses
        #ips = re.findall(pat,line)     
                                                                                                                 
        fields=line.split(" ")
        print fields                            # locate username
        msg = ' '.join(fields[5:])
        
        #username = fields[8]    
                                                                                                                                         
        #srcIP   = ips[0]
        #dstIP   = "HPOT"
        #srcPort = "-1"                                                  # not present in the syslog
        #dstPort = "22"
        #proto   = "6"                                                   # Tevent   = "user=" + username                                    # todo : parse the user     
                                                                                                                                                                                         
        # Get OS type of SRC IP    
        #p0fInfo = p0fcmd.getP0fInfo(srcIP,"0",dstIP,dstPort);           # 0 = wildcard the srcPort
        #if p0fInfo['result'] == True :                                  # p0f data is available   
        #    os   = p0fInfo['genre']
        #    nat  = p0fInfo['nat'][0]
        #else:
        #    os =  "?"
        #    nat = "?"
        
        # Get DNS info
        #dnsInfo = ipintellib.ip2name(srcIP)
        #dnsName = dnsInfo['name'].rstrip('.')                   # right-strip the trailing .
        
        # WHOIS         
        #asInfo = ipintellib.ip2asn(srcIP)                               # 
        #asNum = asInfo['as']		                                # AS123   
        #asRegisteredCode = asInfo['registeredCode']                     # Short-form e.g.ARCOR
 
        # GeoIP information - faster than WHOIS for looking up Country Code information
        #geoIP = ipintellib.geo_ip(srcIP)                                
        #countryCode = geoIP['countryCode']                              
        #city        = geoIP['city']
        #longitude   = geoIP['longitude']                                # Used to calc approx. localtime
        #latitude    = geoIP['latitude']    

        msg  = "Password change : " + msg
                
        print "tweet before compression : " + msg
        sendTweet(msg)
    
    except Exception,e:
        syslog.syslog("kojoney_tweet.py : processSecure() exception caught = " + `e` + " line=" + line)


                                         
# process sebek raw file 
# line = line read from raw sebek logs
def processSebekTweet(line):
    
    ftpInfo = {}
    
    line=line.strip("\n")
    print "entered processSebekTweet() with line=" + line

    try:
        filtered = filter_sebek.filterSebek(line)
        print "processSebekTweet() : filtered = " + filtered
        
        # missing step is to normalise the sebek line i.e. to remove [BS] etc.

        if len(filtered) > 0 :              
            #msg = "Honeypot access:" + filtered
            msg = filtered
            #print "tweet before compression : " + msg
            sendTweet(msg)
        
            # file needs to be touched - is this the daily file ?
            fpOut = open(r'/home/var/log/kojoney_tail_tweets.csv','a')
            print >> fpOut,msg 
            fpOut.close()
            
            # for sebek lines containing "wget", perform additional analysis on destination URL
            if filtered.find("wget") != -1 :
                print "kojoney_tweet.py : processSebekTweet() : wget found"
                url = extract_url.extractURL(filtered)	# Normalise URL
                o = urlparse(url)
                domain = "127.0.0.1"
                path   = ""
                if o.scheme == 'ftp' :
                    ftpInfo = extract_url.extractDomainFTP(url)
                    domain = ftpInfo['domain']
                    path   = ftpInfo['path']                        
                elif len(url) != 0 :                                                                                                                                                    
                    domain = o.netloc
                    path   = o.path  
            
                # Tweet additional info if a valid URL was found
                if len(url) != 0 :
                    # Get IP from DNS info
                    dnsInfo = ipintellib.ip2name(domain)
                    srcIP   = dnsInfo['name'].rstrip('.')	                   # right-strip the trailing .
        
                    # WHOIS         
                    asInfo = ipintellib.ip2asn(srcIP)                               # 
                    asNum = asInfo['as']		                                # AS123   
                    asRegisteredCode = asInfo['registeredCode']                     # Short-form e.g.ARCOR
 
                    # GeoIP information - faster than WHOIS for looking up Country Code information
                    geoIP = ipintellib.geo_ip(srcIP)                                
                    countryCode = geoIP['countryCode']                              
                    city        = geoIP['city']
                    longitude   = geoIP['longitude']                                # Used to calc approx. localtime
                    #latitude    = geoIP['latitude']    
    
                    msg = "URL_FOUND," + url + "->" + \
                    "IP="     + srcIP +  \
                    ",WHOIS=" + asNum + " (" + asRegisteredCode + ")" + \
                    ",GeoIP=" + countryCode + " " + city + " " + "%.2f" % longitude + "E"
                
                    print msg
                    sendTweet(msg)
                    # file needs to be touched - see above
                    fpOut = open(r'/home/var/log/kojoney_tail_tweets.csv','a')
                    print >> fpOut,msg 
                    fpOut.close()
                    
            # for sebek lines containing an IP address, perform additional analysis
            # only searches for 1 IP address
            pat = r'\d+\.\d+\.\d+\.\d+'             # locate a number of IP addresses
            ips = re.findall(pat,filtered)     
            print "first IP address found = " + `ips[0]`
            if len(ips) != 0 :
                    ip = ips[0]
                    # Get DNS name
                    dnsInfo = ipintellib.ip2name(ip)
                    dnsName = dnsInfo['name'].rstrip('.')	                   # right-strip the trailing .
        
                    # WHOIS         
                    asInfo = ipintellib.ip2asn(ip)                               # 
                    asNum = asInfo['as']		                                # AS123   
                    asRegisteredCode = asInfo['registeredCode']                     # Short-form e.g.ARCOR
 
                    # GeoIP information - faster than WHOIS for looking up Country Code information
                    geoIP = ipintellib.geo_ip(ip)                                
                    countryCode = geoIP['countryCode']                              
                    city        = geoIP['city']
                    longitude   = geoIP['longitude']                                # Used to calc approx. localtime
                    #latitude    = geoIP['latitude']    
    
                    msg = "IP_ADDR_FOUND," + ip + "->" + \
                    "DNS="   + dnsName + \
                    ",WHOIS=" + asNum + " (" + asRegisteredCode + ")" + \
                    ",GeoIP=" + countryCode + " " + city + " " + "%.2f" % longitude + "E"
                
                    print msg
                    sendTweet(msg)
                    # file needs to be touched - see above
                    fpOut = open(r'/home/var/log/kojoney_tail_tweets.csv','a')
                    print >> fpOut,msg 
                    fpOut.close()
                    
                                                                                                                                                                                                                                                         
        else :
            #print "tweet filtered out : " + line
            pass
            
    except Exception,e:
        syslog.syslog("kojoney_tweet.py : processSebekTweet() exception caught = " + `e` + " line=" + line)

def processVisualisationTweet(line):
    #print "entered processVisualisationTweet()"

    try:
        fields=line.split(",")
        #print "processVisualisationTweet() : " + `fields`
        
        # Mandatory AfterGlow fields
        source      = fields[0]
        event       = fields[1]		# e.g. ids , flow , amun , aaa , honeyd
        target      = fields[2]		# e.g. mars
        
        # Handle the "Header" and "DNS" and "IDS_SID_KEY" entries in the .csv file
        if line.find("DroneTracer") != -1 or line.find("RQ:") != -1 or line.find("IDS_SID_KEY") != -1 :
            tweet = source + ", "  + target 
        else :					# Standard 'flow' entris from visualisation file
            asn         = fields[4]		# 
            dns         = fields[7]
            tweet = source + "->[" + event + "]->" + target + " " + asn + " " + dns 
        
        # Compress Tweets
        tweet = tweet.strip('\n')
        tweet = tweet.replace("DRONE_MALWARE_UNDER_TEST","DRONE")
        
        # Send the Tweet
        #print "tweet=" + tweet
        sendTweet(tweet)
        
    except Exception,e:
        syslog.syslog("kojoney_tweet.py : processVisualisationTweet() exception caught = " + `e` + " line=" + line)


# wrapper for sending Tweets
# comment out line status=... to disable actual Twitter API call during testing
def sendTweet(tweet_raw):
    global TweetClient
    
    MAXTWEET_LEN=139			# max chars to send
    
    now = time.time()
    
    print "sendTweet(): raw = " + tweet_raw
    
    try:
        # Anonymise and shorten actual honeypot IP address to HPOT
        #tweet = tweet_raw.replace("172.31.0.67","HPOT")		# e.g. not managed via Honeyd        
        #tweet = tweet_raw.replace("172.31.0.1" ,"HPOT")		# e.g. managed via Honeyd
        #tweet = tweet_raw.replace("192.168.1.9","ROUTER")        
                
        # Try to shorten longer words in Snort messages
        #tweet = tweet.replace("Classification: ","C:") 
        #tweet = tweet.replace("Priority: ","P:") 
        #tweet = tweet.replace("Administrator","Admin") 
        #tweet = tweet.replace("Shellcode","SC") 
        #tweet = tweet.replace("Windows Source","Win")
        #tweet = tweet.replace("Information","Info")
        #tweet = tweet.replace("{TCP}","{T}")
        #tweet = tweet.replace("{ICMP}","{I}")
        #tweet = tweet.replace("{UDP}","{U}")
        #tweet = tweet.replace("(portscan) ","")
        #tweet = tweet.replace("Executable ","Exe ")
        #tweet = tweet.replace("Privilege ","Priv ")
        #tweet = tweet.replace("ATTACK_RESPONSE","ATT_RESP")
        #tweet = tweet.replace("ATTACK-RESPONSES","ATT_RESP")
        #tweet = tweet.replace("Microsoft","M$oft")		# personal spite
        #tweet = tweet.replace("MS ","M$oft ")			# personal spite
        #tweet = tweet.replace("symantec","Symantec")		# grammar
        #tweet = tweet.replace("Unauthenticated","Unauth")
        #tweet = tweet.replace("antivirus","AV")
        #tweet = tweet.replace("download","dload")
        #tweet = tweet.replace("CMD Shell","cmd.exe")		# consistency
        #tweet = tweet.replace("Attempted","Attempt")
        #tweet = tweet.replace("NETBIOS","NBIOS")
        #tweet = tweet.replace("version","ver")
        #tweet = tweet.replace("Request","req")
        #tweet = tweet.replace("overflow","oflow")
        #tweet = tweet.replace("xor","XOR")
        #tweet = tweet.replace("was detected","detected")
        
        #tweet = tweet.replace("Linux","LNX")
        #tweet = tweet.replace("Windows","WIN")
        #tweet = tweet.replace("FreeBSD","FBSD")
        #tweet = tweet.replace("OpenBSD","OBSD")
        #tweet = tweet.replace("NetBSD","NBSD")
        
        #tweet = tweet.replace("signature match","")		# PSAD
        tweet = tweet_raw.replace("crouchr","****")			# AAA logs for router login
            
        # construct and prepend a minimal localtime timestamp : HHMM   
        tuple=time.localtime(now)
        timestamp = "%02d" % tuple.tm_hour + "%02d" % tuple.tm_min    
        tweet = timestamp + "," + tweet
    
        # truncate (concatenate in future ?) long tweets 
        if len(tweet) >= MAXTWEET_LEN:
            tweet=tweet[0:MAXTWEET_LEN]
            tweet=tweet + "+"				# + indicates tweet was truncated
            #syslog.syslog("kojoney_tail.py : sendTweet() msg built [truncated to " + `len(tweet)` + " chars] : tweet=" + tweet)
        else:     
            pass
            #syslog.syslog("kojoney_tail.py : sendTweet() msg built : " + tweet)
            
        # basic visualisation of the Tweets
        #writeSecViz5(tweet)
        
        # Filtering
        # ---------
        #print "Before filtering, tweet=" + tweet
        
        # hack - do not Tweet firewall feeds
        #if tweet_raw.find("FEED") != -1 :
        #    return
        
        # hack - do not Tweet netflow feeds    
        #if tweet_raw.find("flow") != -1 :
        #    return

        # hack - do not Tweet firewall events feeds    
        #if tweet_raw.find("adsl") != -1 :
        #    return
    
        # hack - do not Tweet Voip adapter honeyd     
        if tweet_raw.find("172.31.0.71") != -1 :
            return
    
        # Log all attempts to send Tweets
        print "Tweet to be sent via Twitter API : " + tweet
        fpOut = open(r'/home/var/log/tweets.attempts.log.txt','a')
        print >> fpOut,tweet 
        fpOut.close()

        # ***************************************************************************
        # actually send the Tweet - here is where you disable Tweeting during testing        
        status = TweetClient.PostUpdate(tweet)  
        #status = "tweetDisabledInCode"
        # ***************************************************************************  
        #print "notify     : " + tweet
        syslog.syslog("kojoney_tweet.py : TweetClient.PostUpdate() returned status=" + `status` + " for following Tweet : " + tweet)
            
        # Log the successfully sent Tweets - have a .txt extension so Windoze can open it up
        # bug - need to check the status reurn from TweetClient
        fpOut = open(r'/home/var/log/tweets.log.txt','a')
        print >> fpOut,"TWEET=" + tweet 
        fpOut.close()

        # This is too crude - it is triggering on Cisco p0f
        # send an e-mail if the exploit contains particularly interesting keywords
        #if tweet.find("Cisco") != -1 or tweet.find("Conficker") != -1 or tweet.find("Downadup") != -1 :
        #    statusAlert("Exploit du jour detected",tweet)
        
        # send an e-mail if router command-line is being entered
        #if tweet.find("@RTR") != -1 :
        #    statusAlert("Router honeypot being accessed",tweet)
        
        time.sleep(0.5)					# crude rate limit 
    
    except Exception,e:
        syslog.syslog("kojoney_tweet.py : sendTweet() exception caught = " + `e` + " tweet=" + tweet)

    
                           
# -------------------------------------------------------
        
# Start of code        
        
       
# Make pidfile so we can be monitored by monit        
#pid =  makePidFile("kojoney_tweet")
#if pid == None:
#    syslog.syslog("Failed to create pidfile for pid " + `pid`)
#    sys.exit(0)
#else:
#    syslog.syslog("kojoney_tweet started with pid " + `pid`)
                
# Send an email to say kojoney_tail has started
#now = time.time()
#nowLocal = time.gmtime(now)
###makeMsg(0,"0","system,kojoney_viz started with pid=" + `pid` + " at localtime " + time.asctime(nowLocal))
#a = "kojoney_tweet started with pid=" + `pid`

#statusAlert("*** kojoney_tweet started ***",a)

# Create a connection to Twitter
try:

    TweetClient = twitter.Api(username="honeytweeter",password="fuckfacebook")                
#    TweetClient = twitter.Api(username="richardhcrouch",password="fuckfacebook")                

#    print "Twitter Public Timeline Status messages"
#    statuses = TweetClient.GetPublicTimeline()
#    #print [s.user.name for s in statuses]
#    for s in statuses :
#        print s.user.name

#    print "\nTwitter Timeline for @richardhcrouch :"
#    statuses = TweetClient.GetUserTimeline("richardhcrouch")
#    for s in statuses :
#        print s.text

#    print "\n@richardhcrouch friends :"
#    users = TweetClient.GetFriends()
#    for u in users :
#        print u.name

    #print "Post an invalid GeoTagged Tweet :"
    #status = TweetClient.PostUpdate("TW1 : Banger tweet fail for GeoIP",lat=999,long=999)
    #time.sleep(10)
    
    #print "Post a valid GeoTagged Tweet :"
    #status = TweetClient.PostUpdate("Banger tweet OK for GeoIP",lat=52.0,long=1.0)
    
    print "Post a valid GeoTagged Tweet :"
    lat  = 53.56454
    long = -113.5

    #status = TweetClient.PostUpdate("This is a test Tweet sent using geotap API at epoch " + `time.time()` , lat=53.56454, long=-113.5)
    status = TweetClient.PostUpdate("This is a test Tweet sent using geotap API at epoch " + `time.time()` , lat=lat , long=long)

    #print "Post a very long GeoTagged Tweet :"
    #status = TweetClient.PostUpdate("TW3 : Banger tweet OK for GeoIP 3",lat=53.549999923706052,long=-113.5)

    print "Exiting."

except Exception,e:
    syslog.syslog("kojoney_geoip.py : exception " + `e`)
    
# Set the Kojoney Channel filename to scan
#filename = '/home/var/log/kojoney_tail.log'

# Set the Kojoney Visualisation filename to scan
#filename = '/home/var/log/kojoney_fprint.csv'

# Set the Sebek raw logs filename to scan
#filename = '/home/var/log/sebek.log.txt'
#file = open(filename,'r')

#filenameMessages = '/var/log/messages'
#fileMessages = open(filenameMessages,'r')

#filenameSecure = '/var/log/secure'
#fileSecure = open(filenameSecure,'r')

# ------------
# tail -f mode
# ------------

# Find the size of the Channel file and move to the end
#st_results = os.stat(filename)
#st_size = st_results[6]
#file.seek(st_size)
#print "system     : Seek to end of Sebek raw log feed"

# Look for successful logins
#st_resultsMessages = os.stat(filenameMessages)
#st_sizeMessages = st_resultsMessages[6]
#fileMessages.seek(st_sizeMessages)
#print "system     : Seek to end of /var/log/messsages log feed"

# Look for passwd changes
#st_resultsSecure = os.stat(filenameSecure)
#st_sizeSecure = st_resultsSecure[6]
#fileSecure.seek(st_sizeSecure)
#print "system     : Seek to end of /var/log/secure log feed"

#while True:
    
    # Kojoney Channel       
#    where = file.tell()
#    line  = file.readline()
    
    # /var/log/messages
#    whereMessages = fileMessages.tell()
#    lineMessages  = fileMessages.readline()
    
    # /var/log/secure
#    whereSecure = fileSecure.tell()
#    lineSecure  = fileSecure.readline()
    
#    if not line:		# no data in Kojoney Channel
        #print "nothing in Kojoney Channel logfile to process"
#        file.seek(where)
#    else :			# new data has been added to log file
        #print "*** NEW EVENT in Kojoney Channel to process !"
        #processChannelTweet(line) - very old - do not use
        #processVisualisationTweet(line) - too verbose - add another twitter account to handle this feed
 #       processSebekTweet(line)
        
#    if not lineMessages:		# no data in Kojoney Channel
        #print "nothing in Kojoney Channel logfile to process"
#        fileMessages.seek(whereMessages)
#    else :			# new data has been added to log file
        #print "*** NEW EVENT in Kojoney Channel to process !"
        #processChannelTweet(line) - very old - do not use
        #processVisualisationTweet(line) - too verbose - add another twitter account to handle this feed
#        processMessages(lineMessages)
    
#    if not lineSecure:		# no data in Kojoney Channel
        #print "nothing in Kojoney Channel logfile to process"
#        fileSecure.seek(whereSecure)
#    else :			# new data has been added to log file
        #print "*** NEW EVENT in Kojoney Channel to process !"
        #processChannelTweet(line) - very old - do not use
        #processVisualisationTweet(line) - too verbose - add another twitter account to handle this feed
#        processSecure(lineSecure)
        
    #print "sleeping..."
    # this can be a float for sub-second sleep    
#    time.sleep(0.2)	# 0.1 second
                              
                                                                 