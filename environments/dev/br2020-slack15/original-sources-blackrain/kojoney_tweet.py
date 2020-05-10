#!/usr/bin/python

# Tail the Kojoney Channel and send out Tweets

import time, os , syslog , re , sys 
#import twitter		# Google API python-twitter 

import tweepy

from urlparse import urlparse
from ConfigParser import ConfigParser

import ipintellib				# RCH library - master on mars
import mailalert				# RCH library
import p0fcmd					# RCH library - master on mars
import filter_sebek     			# RCH library - master on mars
import extract_url      			# RCH library - master on mars
import kojoney_ossec_parse		  	# RCH library - master on mars
import kojoney_amun_parse			
import kojoney_glastopf_parse			
import kojoney_pads_parse			
import kojoney_kippo_parse			
import kojoney_clamd_parse			# contains virii signatures found by clsniffer			
import kojoney_telnetd_parse			
import kojoney_spamhole_parse			
import kojoney_passer_parse			
import kojoney_iplog_parse			
import kojoney_honeytrap_parse			
import kojoney_honeyd_parse			
import kojoney_suricata_parse			
import kojoney_shadow_snort_parse			
import kojoney_fwsnort_parse			
import kojoney_spade_parse			
import kojoney_bro_parse			
import kojoney_argus_parse			
import kojoney_aaa_parse			
import kojoney_p0f_parse			
import kojoney_maldet_parse
import kojoney_tsom_parse
import kojoney_conpot_parse

import kojoney_netmenaces_idmef			# no Tweeting - just  IDMEF alert generation

#import kojoney_guru_parse			
import kojoney_router_parse			
import kojoney_funcs			
import twitter_funcs				# RCH library

# Hooks to use Blackrain BRX
import BlackRainClient				# BRX API
import blackrain_logging
import kojoney_blackrain
import kojoney_netflow_parse
import logging

#ROUTER = "172.31.0.9"
HPOT   = "172.31.0.67"
HONEYD = "172.31.0.1"

IBG    = "172.31.0.47"	# IP address sending netflow 

TweetId = 0		# increment so each Tweet is not the same - Twitter API rejects identical ones

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
    destination  = ['ipbb.mvtc@googlemail.com']
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
        #print "processChannelTweet() : " + `fields`
        
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



#2011-01-07 21:00:16+0000 [SSHChannel session (0) on SSHService ssh-connection on HoneyPotTransport,1,192.168.1.75] Opening TTY log: log/tty/20110107-210016-9013.log
#2011-01-07 21:00:46+0000 [SSHChannel session (0) on SSHService ssh-connection on HoneyPotTransport,1,192.168.1.75] CMD: who
#2011-01-07 21:00:46+0000 [SSHChannel session (0) on SSHService ssh-connection on HoneyPotTransport,1,192.168.1.75] Command found: who
#2011-01-07 21:00:59+0000 [SSHChannel session (0) on SSHService ssh-connection on HoneyPotTransport,1,192.168.1.75] CMD: top
#2011-01-07 21:00:59+0000 [SSHChannel session (0) on SSHService ssh-connection on HoneyPotTransport,1,192.168.1.75] Command not found: top
#2011-01-07 21:01:01+0000 [SSHChannel session (0) on SSHService ssh-connection on HoneyPotTransport,1,192.168.1.75] CMD: ls
#2011-01-07 21:01:01+0000 [SSHChannel session (0) on SSHService ssh-connection on HoneyPotTransport,1,192.168.1.75] Command found: ls
#2011-01-07 21:01:03+0000 [SSHChannel session (0) on SSHService ssh-connection on HoneyPotTransport,1,192.168.1.75] CMD: pwd
#2011-01-07 21:01:03+0000 [SSHChannel session (0) on SSHService ssh-connection on HoneyPotTransport,1,192.168.1.75] Command found: pwd
#2011-01-07 21:01:06+0000 [SSHChannel session (0) on SSHService ssh-connection on HoneyPotTransport,1,192.168.1.75] CMD: id
#2011-01-07 21:01:06+0000 [SSHChannel session (0) on SSHService ssh-connection on HoneyPotTransport,1,192.168.1.75] Command found: id
#def processKippo(line):
#
#    try :
#        line=line.strip("\n")
#        print "processKippo() : line received from Honeypot : " + line
#        
#        # log failed attempted passwords to a file            
#        if line.find("login attempt") != -1:
#            fields = line.split(" ")
#            print fields
#            msg = ' '.join(fields[5:])
#            
#            now      = time.time()
#            nowLocal = time.localtime(now)
#            msg = time.asctime(nowLocal) + " : " + msg
#            print msg
#            
#            fp = open("/home/var/log/kippo_failed_attempts.log",'a')
#            print >> fp, msg
#            fp.close()
#            
#        
#        if (line.find("Opening TTY log") == -1 and line.find("CMD:") == -1) :         # can't find the interesting entries so return 
#           return None
#            
#        print "processKippo() : candidate syslog read from Honeypot : " + line
#                                                                                 
#        fields = line.split()
#        print fields
#        
#        uid = "0"		# Kippo only supports a root account
#        a = fields[9].rstrip(']')
#        srcip = a.split(',')[2]
#        print "attacker IP : " + srcip
#        
#        # INT = intrusion
#        if line.find("Opening TTY log") != -1:
#            tweet = "KIPPO_INT," + "login from " + srcip + " to be logged in " + fields[13] 
#        else:
#            cmd = ' '.join(fields[11:])
#            #cmd = 'rch testing - ignore'
#            print cmd
#        
#            # fake the correct shell prompt
#            if uid == "0" :
#                prompt = "#"
#            else:
#                prompt = "$"
#            #tweet = "--,KIPPO,UID:" + uid + " {sshd} " + prompt + " " + cmd	# fake the GeoIP of src (unknown)
#            tweet = "KIPPO,UID:" + uid + " {sshd} " + prompt + " " + cmd	# fake the GeoIP of src (unknown)
#        
#        print "processKippo() : tweet=" + tweet 
#        return tweet
#    
#    except Exception,e:
#        syslog.syslog("kojoney_tweet.py : processKippo() exception caught = " + `e` + " line=" + line)

# /var/log/messages
# syslogs from honeypot itself
#Sep 28 06:19:28 mars T=2010-09-28__06:19:25  PI=912 UI=0 pwd
#Sep 28 06:19:28 mars T=2010-09-28__06:19:26  PI=912 UI=0 ls
#Sep 28 06:19:31 mars T=2010-09-28__06:19:29  PI=912 UI=0 top
#Sep 28 06:19:33 mars T=2010-09-28__06:19:31  PI=912 UI=0 ls
#Sep 28 06:19:35 mars T=2010-09-28__06:19:33  PI=912 UI=0 exit   
def processKeystrokes(line):

    try :
        line=line.strip("\n")
        print "processKeystrokes() : line received from Honeypot : " + line
                    
        if line.find("T=201") == -1 :         # find trojan bash anchor - not a very good one 
            return
            
        print "processKeystrokes() : candidate syslog read from Honeypot : " + line
                                                                                 
        fields=line.split()
        #print fields
        
        pid = fields[5].split("=")[1]
        uid = fields[6].split("=")[1]
        cmd = ' '.join(fields[7:])
        
        # fake the correct shell prompt
        if uid == "0" :
            prompt = "#"
        else:
            prompt = "$"
        
        msg = "UID:" + uid + " PID:" + pid + " {bash}\n" + prompt + " " + cmd
        #print msg
                
        print "tweet before compression : " + msg
        sendTweet(msg)
    
    except Exception,e:
        syslog.syslog("kojoney_tweet.py : processKeystrokes() exception caught = " + `e` + " line=" + line)

#May 10 06:48:30 mars sshd[1122]: Accepted password for test from 172.31.0.68 port 1028 ssh2 
#May 10 08:52:50 mars sshd[1291]: Failed password for test from 172.31.0.68 port 1029 ssh2 
#May 10 08:52:52 mars sshd[1291]: Accepted password for test from 172.31.0.68 port 1029 ssh2 
#May 10 14:26:15 mars sshd[9525]: Accepted password for crouchr from 192.168.1.248 port 49918 ssh2
def processMessages(line):

    try :
        line=line.strip("\n")
        print "processMessages() : line read from Honeypot syslogs : " + line
                    
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
        sendTweet(msg,lat=latitude,long=longitude)
        
        # Modify the defcon number 
        kojoney_funcs.writeDefconEvent("botwall","intrusion from " + srcIP + " account=" + username) 
    
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

        msg  = "PASSWD_CHANGE," + msg
                
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
                    print "kojoney_tweet.py : processSebekTweet() : IP=" + srcIP
                
                    # WHOIS         
                    asInfo = ipintellib.ip2asn(srcIP)                               # 
                    asNum = asInfo['as']		                                # AS123   
                    asRegisteredCode = asInfo['registeredCode']                     # Short-form e.g.ARCOR
                    print "kojoney_tweet.py : processSebekTweet() : AS name=" + asRegisteredCode
 
                    # GeoIP information - faster than WHOIS for looking up Country Code information
                    geoIP = ipintellib.geo_ip(srcIP)                                
                    countryCode = geoIP['countryCode']                              
                    city        = geoIP['city']
                    longitude   = geoIP['longitude']                                # Used to calc approx. localtime
                    latitude    = geoIP['latitude']    
    
                    # Is this too long when geotag nfo ia added ?
                    #msg = "URL_FOUND," + url + "->" + \
                    #"IP="     + srcIP +  \
                    #",WHOIS=" + asNum + " (" + asRegisteredCode + ")" + \
                    #",GeoIP=" + countryCode + " " + city + " " + "%.2f" % longitude + "E"
                    
                    # You don't need city & longitude in tweet since Twitter adds this information
                    msg = "URL_FOUND," + url + " -> " + \
                    "IP="     + srcIP + \
                    "," + asNum + " (" + asRegisteredCode + ")" + \
                    ",CC=" + countryCode
                    # + " " + city + " " + "%.2f" % longitude + "E"

                    #msg = "test message 2"                
                    print msg
                    
                    sendTweet(msg,lat=latitude,long=longitude)
                    # file needs to be touched - see above
                    fpOut = open(r'/home/var/log/kojoney_tail_tweets.csv','a')
                    print >> fpOut,msg + ":lat=" + `latitude` + " long=" + `long` 
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
                    asInfo = ipintellib.ip2asn(ip)   	                            # 
                    asNum = asInfo['as']		                                # AS123   
                    asRegisteredCode = asInfo['registeredCode']                     # Short-form e.g.ARCOR
 
                    # GeoIP information - faster than WHOIS for looking up Country Code information
                    geoIP = ipintellib.geo_ip(ip)                                
                    countryCode = geoIP['countryCode']                              
                    city        = geoIP['city']
                    longitude   = geoIP['longitude']                                # Used to calc approx. localtime
                    latitude    = geoIP['latitude']    
    
                    msg = "IP_ADDR_FOUND," + ip + " -> " + \
                    "DNS="   + dnsName + \
                    "," + asNum + " (" + asRegisteredCode + ")" + \
                    ",CC=" + countryCode
                    # + " " + city + " " + "%.2f" % longitude + "E"
                
                    print msg
                    sendTweet(msg,lat=latitude,long=longitude)
                    # file needs to be touched - see above
                    fpOut = open(r'/home/var/log/kojoney_tail_tweets.csv','a')
                    print >> fpOut,msg + ":lat=" + `latitude` + " long=" + `long` 
                    #print >> fpOut,msg 	# bug - add GeoIP information
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
        twitter_funcs.sendTweet(tweet,"honeytweeter")
        
    except Exception,e:
        syslog.syslog("kojoney_tweet.py : processVisualisationTweet() exception caught = " + `e` + " line=" + line)

# Wrapper
# Extract first non-honeypot IP from a Tweet
# Perform GeoIP on IP to get lat/long
# Call SendTweet() to send the Tweet
# Assumes that Tweet has had honeypot IPs converted to text not IP addresses
#def sendGeoIPTweet(tweet_raw) :
#    try :
#        latitude  = None
#        longitude = None
#        tweet = tweet_raw
#        metaData = None
#        
#        pat = r'\d+\.\d+\.\d+\.\d+'             # locate a number of IP addresses
#        ips = re.findall(pat,tweet)     
#        if len(ips) != 0 :
#            ip = ips[0]
#            #print "sendGeoIPTweet(): first IP address found & will be used for geolocation = " + ip
#        
#            # Get DNS name
#            #dnsInfo = ipintellib.ip2name(ip)
#            #dnsName = dnsInfo['name'].rstrip('.')	                   # right-strip the trailing .
#        
#            # WHOIS         
#            #asInfo = ipintellib.ip2asn(ip)   	                            # 
#            #asNum = asInfo['as']		                                # AS123   
#            #asRegisteredCode = asInfo['registeredCode']                     # Short-form e.g.ARCOR
# 
#            # GeoIP information - faster than WHOIS for looking up Country Code information
#            geoIP = ipintellib.geo_ip(ip)                                
#            countryCode = geoIP['countryCode']                              
#            city        = geoIP['city']
#            longitude   = geoIP['longitude']                                # Used to calc approx. localtime
#            latitude    = geoIP['latitude']    
#            
#            metaData = "cc=" + countryCode + "," + "city=" + city
#            if countryCode == 'None':
#                tweet = "--" + "," + tweet_raw
#            else:
#                tweet = countryCode + "," + tweet_raw
#                
#        sendTweet(tweet,lat=latitude,long=longitude,meta=metaData)
#    
#    except Exception,e:
#        syslog.syslog("kojoney_tweet.py : sendGeoIPTweet() exception caught = " + `e` + " tweet_raw=" + tweet_raw)

# --------------------------------------

# wrapper for sending Tweets
# comment out line status=... to disable actual Twitter API call during testing
# add support for selecting the account to use
# meta = whatever cvs info to append to the Tweet log (does not get tweeted)
# tweet = tweet[:::]
# inband parameter : if ":::" is present (at the end of the tweet) then do not send the tweet via the API, only log it
#
#def sendTweet(tweet_raw,lat=None,long=None,meta=None):
#    global TweetClient
#    global TweetId
#    
#    if tweet_raw == None:
#        return
#    
#    tweet_raw = tweet_raw.rstrip("\n")	# Ensure no trailing \n characters
#    
#    MAXTWEET_LEN = 137			# max chars to send
#    
#    now = time.time()
#    
#    print "sendTweet(): entered function, tweet_raw = " + tweet_raw + ", lat=" + `lat` + " long=" + `long`
#
#    # Don't actually send honeyd tweets for the moment - too noisy
#    #if tweet_raw.find("HONEYD") != -1:
#    #    return
#
#    CONSUMER_KEY    = 'N4EpgHKzFe5tf6mqmYqJQ'
#    CONSUMER_SECRET = 'Vr7Mxg6GdwY70a4w29ClKCqaD5w4BI7gqWPd0G1ME'
#    
#    ACCESS_KEY      = '19196850-M2WmOBV1voMyFixfBaIJtJ5ol2ntihTte1lCxxRda'
#    ACCESS_SECRET   = '9kWZw7JYrtNcCGpwhYb2qIsGgSqG88cCCUjjcYMwoE'
#     
#    try:
#        if (lat != None and long != None) :
#            lat  = '%.2f' % lat	    # truncate to 2 decimal points as required by Twitter
#            long = '%.2f' % long    # truncate to 2 decimal points as required by Twitter
#        
#        #print "sendTweet() : after truncation to 2 decimal points, lat=" + `lat` + " long=" + `long` 
#        
#       # If GeoIP failed, then set to None so as not to have Tweepy reject the API call - hypothesis at the moment
#        if lat == '999.00' or long == '999.00' :
#            #print "send_tweet() : no geoip information obtained"
#            lat = None
#            long = None
#        
#        # Low-level override of anything performed by crouchr account
#        tweet = tweet_raw.replace("crouchr"   , "***")			# AAA logs for router login
#        tweet = tweet_raw.replace("s0lab0sch" , "***")			# 
#        tweet = tweet_raw.replace("trisfmotp" , "***")			# 
#    
#        # prepend TweetId to prevent duplicate Tweets and to check how reliable the tweet API is 
#        #tweet = "id" + `TweetId` + "," + tweet
#        TweetId = TweetId + 1 
#            
#        # prepend a minimal localtime timestamp : HHMM   
#        tuple=time.localtime(now)
#        timestamp = "%02d" % tuple.tm_hour + ":" + "%02d" % tuple.tm_min    
#        tweet = timestamp + "," + tweet
#      
#        # truncate (concatenate in future ?) long tweets 
#        if len(tweet) >= MAXTWEET_LEN:
#            tweet=tweet[0:MAXTWEET_LEN]
#            tweet=tweet + "..."				# + indicates tweet was truncated
#            #syslog.syslog("kojoney_tail.py : sendTweet() msg built [truncated to " + `len(tweet)` + " chars] : tweet=" + tweet)
#        else:     
#            pass
#            #syslog.syslog("kojoney_tail.py : sendTweet() msg built : " + tweet)
#            
#        # basic visualisation of the Tweets
#        #writeSecViz5(tweet)
#        
#      
#        # Log all attempts to send Tweets - before using the API (in case the Twitter API fails)
#        
#        if meta != None:
#            metaData = "," + meta
#        else:
#            metaData = ""    
#        msg = tweet + ",lat=" + `lat` + "," + "long=" + `long` + metaData + "," + timestamp 
#        print msg
#        
#        fpOut = open(r'/home/var/log/tweets.attempts.log.txt','a')
#        print >> fpOut,`TweetId` + "," + msg 
#        fpOut.close()
#
#        # ******************************************************************************************
#        # actually send the Tweet - here is where you disable Tweeting during testing
#        # You need to enable the Tweet account for geotagging under Settings tab on Twitter Web page        
#        # ******************************************************************************************     
#        if tweet.find(":::") == -1 :	# ":::" at end of tweet == do not tweet via API
#            auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
#            auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
#            api = tweepy.API(auth)
#            api.update_status(tweet,lat=lat,long=long)
#    
#            fpOut = open(r'/home/var/log/tweets.log.txt','a')
#            print >> fpOut,`TweetId` + "," + "TWEET=" + tweet + ",lat=" + `lat` + " long=" + `long` 
#            fpOut.close()
#    
#            time.sleep(0.5)	# crude rate limit into Twitter 
#    
#    except Exception,e:
#        syslog.syslog("kojoney_tweet.py : sendTweet() exception caught = " + `e` + " tweet_raw=" + tweet_raw)
#
#
# HIDS + Amun
#def processSagan(line):
#    try :
#        line = line.rstrip("\n")
#        #if line.find("Message: snort") != -1 :
#            
#            # Filter out noisy alerts e.g SSH brutefore messages
#        #    if line.find(":2006435:") != -1 :
#        #        return None
#        #    if line.find(":2001219:") != -1 :
#        #        return None
#                
#            # event is interesting so create Tweet    
#        fields = line.split(" ")
#        msg = ' '.join(fields[2:])
#        tweet = "HIDS," + msg
#        tweet = twittify(tweet)   
#        return tweet
#        
#        #return None
#    
#    except Exception,e:
#        syslog.syslog("kojoney_tweet.py : processSagan() exception caught = " + `e` + " line=" + line)

def processSnort(line):
    try :
        line = line.rstrip("\n")
        print "line=" + line
        #if line.find("Message: snort") != -1 :
            
            # Filter out noisy alerts e.g SSH brutefore messages
        if line.find(":2006435:") != -1 :
            return None
        if line.find(":2001219:") != -1 :
            return None
                
        # event is interesting so create Tweet    
        fields = line.split(" ")
        msg = ' '.join(fields[6:])
        tweet = msg
        tweet = twittify(tweet)   
        return tweet
        
        #return None
    
    except Exception,e:
        syslog.syslog("kojoney_tweet.py : processSnort() exception caught = " + `e` + " line=" + line)

# Suricata IDS events
# this is superceded
#def processSur(line):
#    try :
#        line = line.rstrip("\n")
#        print "line=" + line
#        
#        if line.find("NIDS_SU") == -1 :
#            return None
#                    
#        # !!! : proper way is to do the filtering in suricata config - do it here for the  moment            
#        
#        # drop uninteresting events
#        if line.find(":2010937:") != -1:
#            return
#        if line.find(":2010935:") != -1:		# mssql tcp 1433 is frequent
#            return
#        
#        # 2 identical alerts for same signature
#        if line.find(":1448:") != -1:			# MS terminal server tcp 3389
#            return
#                    
#        # event is interesting so create Tweet    
#        #fields = line.split(" ")
#        #print fields
#        #msg = ' '.join(fields[5:])
#        #tweet = msg
#        
#        tweet = twittify(tweet)   
#        return tweet
#        
#        #return None
#    
#    except Exception,e:
#        syslog.syslog("kojoney_tweet.py : processSur() exception caught = " + `e` + " line=" + line)

def processNetflow(line):
    try :
        line = line.rstrip("\n")
        print "kojoney_tweey.py : processNetflow() line=" + line
        #if line.find("Message: snort") != -1 :
            
        if line.find("exception caught") != -1 :
            return None
        
        if line.find(" 172.30.0.2 ") != -1 :	# ignore DNS requests from honeypot to my DNS server
            return None
            
        # Only process outbound flows
        # search covers "flowtrain started" and "flowtrain ended" events     
        if line.find(" flowtrain ") == -1 :
            return None
            
        # Do not log HPOT response flows to port 80 Web scans / brute force attempts
        if line.find(" sp=80 ") != -1 :
            return None

        # Do not log HPOT response flows (ICMP ping reponse) to ICMP echo requests (probes)
        if line.find(" sp=0 ") != -1  and line.find("ICMP" ) != -1 and line.find(" dp=0 ") != -1 :
            return None

        # Do not log HPOT response flows to port 110  scans / brute force attempts
        if line.find(" sp=110 ") != -1 :
            return None
        
        # Do not log HPOT response flows to port 8080 Web scans / brute force attempts
        if line.find(" sp=8080 ") != -1 :
            return None
        
        # Do not log HPOT response flows to SSH scans / brute force attempts
        if line.find(" sp=22 ") != -1 :
            return None
        
        # Do not log HPOT response flows to Telnet scans / brute force attempts
        if line.find(" sp=23 ") != -1 :
            return None
        
        # Do not log HPOT response flows to FTP scans / brute force attempts
        if line.find(" sp=21 ") != -1 :
            return None

        # Do not log HPOT response flows to Windows scans / brute force attempts
        if line.find(" sp=445 ") != -1 :
            return None

        # Do not log HPOT response flows to Windows scans / brute force attempts
        if line.find(" sp=135 ") != -1 :
            return None

        # Do not log HPOT response flows to Windows scans / brute force attempts
        if line.find(" sp=139 ") != -1 :
            return None
                        
        # event is interesting so create Tweet    
        fields = line.split(" ")
        print fields
        msg = ' '.join(fields[5:])
        tweet = msg
        tweet = twittify(tweet)   
        return tweet
        
        #return None
    
    except Exception,e:
        syslog.syslog("kojoney_tweet.py : processNetflow() exception caught = " + `e` + " line=" + line)

# Tweet all defcon changes for the time being
def processDefcon(line):
    try :
        line = line.rstrip("\n")
        print "kojoney_tweet.py : processDefcon() line=" + line
            
        #if line.find("exception caught") != -1 :
        #    return None
          
        # event is interesting so create Tweet    
        #fields = line.split(" ")
        #print fields
        #msg = ' '.join(fields[5:])
        tweet = "betaCode!:" + line
        tweet = twittify(tweet)   
        return tweet
        
        #return None
    
    except Exception,e:
        syslog.syslog("kojoney_tweet.py : processNetflow() exception caught = " + `e` + " line=" + line)

                
# -------------        
# Start of code        
# -------------
syslog.openlog("kojoney_tweet",syslog.LOG_PID,syslog.LOG_LOCAL2)		# Set syslog program name        
       
# Make pidfile so we can be monitored by monit        
pid =  makePidFile("kojoney_tweet")
if pid == None:
    syslog.syslog("Failed to create pidfile for pid " + `pid`)
    sys.exit(0)
else:
    syslog.syslog("kojoney_tweet.py started with pid " + `pid`)
                
# Send an email to say kojoney_tail has started
now = time.time()
nowLocal = time.gmtime(now)
#makeMsg(0,"0","system,kojoney_viz started with pid=" + `pid` + " at localtime " + time.asctime(nowLocal))
a = "kojoney_tweet started with pid=" + `pid`

# ------------ BRX --------------
blackrain_logging.setLogging(mode='a')
logging.info("Started")

sensorId = "0080c7886b71"	# MAC address of mars node
#sensorId = "000c29a1dd89"	# MAC address of mars node

# Establish session to BRX
# This is controlled by a retry schedule
kojoney_blackrain.loginToBRX(sensorId)

# ------------ BRX --------------

# Set the Sebek raw logs filename to scan
#filename = '/home/var/log/sebek.log.txt'
#file = open(filename,'r')

filenameMessages = '/home/var/log/honeypot.syslog'
fileMessages = open(filenameMessages,'r')

#filenameOssec = '/var/ossec/logs/alerts/alerts.log'
filenameOssec = '/home/var/log/ossec.log'
fileOssec = open(filenameOssec,'r')

filenameClamd = '/home/var/log/clamd.syslog'
fileClamd     = open(filenameClamd,'r')

filenameKippo = '/home/var/log/kippo.log'
fileKippo = open(filenameKippo,'r')

filenameTSOM = '/home/var/log/tsom_dump.csv'
fileTSOM     = open(filenameTSOM,'r')

filenameTelnet = '/home/var/log/faketelnetd.log'
fileTelnet     = open(filenameTelnet,'r')

filenameAmunSubmit = '/usr/local/src/amun/logs/submissions.log'
fileAmunSubmit     = open(filenameAmunSubmit,'r')

filenameAmunExploit = '/usr/local/src/amun/logs/exploits.log'
fileAmunExploit     = open(filenameAmunExploit,'r')

filenameAmunDownload = '/usr/local/src/amun/logs/successfull_downloads.log'
fileAmunDownload     = open(filenameAmunDownload,'r')

filenameGlastopf     = '/usr/local/src/glastopf/log/glastopf.log'
fileGlastopf         = open(filenameGlastopf,'r')

filenamePads         = '/home/var/log/pads-assets.csv'
filePads             = open(filenamePads,'r')

filenamePasser       = '/home/var/log/passer.csv'
filePasser           = open(filenamePasser,'r')

filenameIplog        = '/home/var/log/iplog.log'
fileIplog            = open(filenameIplog,'r')

filenameMaldet       = '/usr/local/maldetect/event_log'
fileMaldet           = open(filenameMaldet,'r')

filenameHoneytrap    = '/home/var/log/honeytrap.log'
fileHoneytrap        = open(filenameHoneytrap,'r')

filenameSagan        = '/var/log/sagan/alert'
fileSagan            = open(filenameSagan,'r')

# internal IDS
filenameSnort        = '/home/var/log/snort.syslog'
fileSnort            = open(filenameSnort,'r')

# Twitter honeypot #1
filenameNetmenaces   = '/home/var/log/ext-hpot-netmenaces.log'
fileNetmenaces       = open(filenameNetmenaces,'r')

# Twitter honeypot #2
filenameEvilafoot    = '/home/var/log/ext-hpot-evilafoot.log'
fileEvilafoot        = open(filenameEvilafoot,'r')

# internal IDS
filenameSur          = '/home/var/log/suricata.syslog'
fileSur              = open(filenameSur,'r')

# external IDS
filenameShadowSnort  = '/home/var/log/shadow_ids.syslog'
fileShadowSnort      = open(filenameShadowSnort,'r')

# external ADS - Snort Spade
filenameSpadeSnort  = '/home/var/log/spade.syslog'
fileSpadeSnort      = open(filenameSpadeSnort,'r')

# fwsnort
filenameFwSnort      = '/home/var/log/fwsnort.syslog'
fileFwSnort          = open(filenameFwSnort,'r')

#filenameHoneyd       = '/home/var/log/honeyd.log'
filenameHoneyd       = '/home/var/log/honeyd.syslog'
fileHoneyd           = open(filenameHoneyd,'r')

#filenameNetflow      = '/home/var/log/netflow_correlated_events.log'
filenameNetflow      = '/home/var/log/netflow.syslog'
fileNetflow          = open(filenameNetflow,'r')

filenameDefcon       = '/home/var/log/defcon_events2.log'
fileDefcon           = open(filenameDefcon,'r')

filenameArgus        = '/home/var/log/argus.log'
fileArgus            = open(filenameArgus,'r')

filenameSpam         = '/home/var/log/spamhole.syslog'
fileSpam             = open(filenameSpam,'r')

# performance issues - so remove for the ime being Nov 2011
#filenameBroCon       = '/usr/local/bro/logs/current/conn.log'
#fileBroCon           = open(filenameBroCon,'r')

# Router AUTHENTICATION
filenameAuth         = '/home/var/log/tacacs.syslog'
fileAuth             = open(filenameAuth,'r')

# Router ACCOUNTING
filenameAcct         = '/home/var/log/tacacs.log'
fileAcct             = open(filenameAcct,'r')

filenamep0f         = '/home/var/log/p0f.log'
filep0f             = open(filenamep0f,'r')

#filenameguru        = '/home/var/log/kojoney_guru.txt'
#fileguru            = open(filenameguru,'r')

filenamerouter      = '/home/var/log/honeyrtr.syslog'
filerouter          = open(filenamerouter,'r')

filenamerouterv6    = '/home/var/log/honeyrtrv6.syslog'
filerouterv6        = open(filenamerouterv6,'r')

filenameConpot      = '/home/var/log/conpot.syslog'
fileConpot          = open(filenameConpot,'r')

# ------------
# tail -f mode
# ------------

# Find the size of the Sebek file and move to the end
#st_results = os.stat(filename)
#st_size = st_results[6]
#file.seek(st_size)
#print "system     : Seek to end of Sebek raw log feed " + filename

# Look for successful logins and passwd changes and keystrokes from honeypot syslogs
st_resultsMessages = os.stat(filenameMessages)
st_sizeMessages = st_resultsMessages[6]
fileMessages.seek(st_sizeMessages)
print "system     : Seek to end of " + filenameMessages

# Look for HIDS events in Ossec alerts log file
st_resultsOssec = os.stat(filenameOssec)
st_sizeOssec = st_resultsOssec[6]
fileOssec.seek(st_sizeOssec)
print "system     : Seek to end of " + filenameOssec

# Look for ClamAV events
st_resultsClamd = os.stat(filenameClamd)
st_sizeClamd = st_resultsClamd[6]
fileClamd.seek(st_sizeClamd)
print "system     : Seek to end of " + filenameClamd

# Look for session data in Argus log file
st_resultsArgus = os.stat(filenameArgus)
st_sizeArgus = st_resultsArgus[6]
fileArgus.seek(st_sizeArgus)
print "system     : Seek to end of " + filenameArgus

# Look for SMTP session data in Spamholed log file
st_resultsSpam = os.stat(filenameSpam)
st_sizeSpam = st_resultsSpam[6]
fileSpam.seek(st_sizeSpam)
print "system     : Seek to end of " + filenameSpam

# Look for events in Kippo log file
st_resultsKippo = os.stat(filenameKippo)
st_sizeKippo = st_resultsKippo[6]
fileKippo.seek(st_sizeKippo)
print "system     : Seek to end of " + filenameKippo

# Look for events in TSOM Threat Level Calculation log file
st_resultsTSOM = os.stat(filenameTSOM)
st_sizeTSOM = st_resultsTSOM[6]
fileTSOM.seek(st_sizeTSOM)
print "system     : Seek to end of " + filenameTSOM

# Look for events in Telnet log file
st_resultsTelnet = os.stat(filenameTelnet)
st_sizeTelnet    = st_resultsTelnet[6]
fileTelnet.seek(st_sizeTelnet)
print "system     : Seek to end of " + filenameTelnet

# Look for Amun malware analysis malware analysis submissions
st_resultsAmunSubmit = os.stat(filenameAmunSubmit)
st_sizeAmunSubmit = st_resultsAmunSubmit[6]
fileAmunSubmit.seek(st_sizeAmunSubmit)
print "system     : Seek to end of " + filenameAmunSubmit

# Look for Amun malware analysis exploit messages
st_resultsAmunExploit = os.stat(filenameAmunExploit)
st_sizeAmunExploit    = st_resultsAmunExploit[6]
fileAmunExploit.seek(st_sizeAmunExploit)
print "system     : Seek to end of " + filenameAmunExploit

# Look for Amun successful download attempts
st_resultsAmunDownload = os.stat(filenameAmunDownload)
st_sizeAmunDownload    = st_resultsAmunDownload[6]
fileAmunDownload.seek(st_sizeAmunDownload)
print "system     : Seek to end of " + filenameAmunDownload

# Look for Glastopf web attacks
st_resultsGlastopf = os.stat(filenameGlastopf)
st_sizeGlastopf    = st_resultsGlastopf[6]
fileGlastopf.seek(st_sizeGlastopf)
print "system     : Seek to end of " + filenameGlastopf

# Look for PADS discovered assets
st_resultsPads = os.stat(filenamePads)
st_sizePads    = st_resultsPads[6]
filePads.seek(st_sizePads)
print "system     : Seek to end of " + filenamePads

# Look for PASSER discovered assets
st_resultsPasser = os.stat(filenamePasser)
st_sizePasser    = st_resultsPasser[6]
filePasser.seek(st_sizePasser)
print "system     : Seek to end of " + filenamePasser

# Look for IPLOG scans
st_resultsIplog  = os.stat(filenameIplog)
st_sizeIplog     = st_resultsIplog[6]
fileIplog.seek(st_sizeIplog)
print "system     : Seek to end of " + filenameIplog

# Look for LMD malware detection
st_resultsMaldet  = os.stat(filenameMaldet)
st_sizeMaldet     = st_resultsMaldet[6]
fileMaldet.seek(st_sizeMaldet)
print "system     : Seek to end of " + filenameMaldet

# Look for remaining probes to honeytrap
st_resultsHoneytrap  = os.stat(filenameHoneytrap)
st_sizeHoneytrap     = st_resultsHoneytrap[6]
fileHoneytrap.seek(st_sizeHoneytrap)
print "system     : Seek to end of " + filenameHoneytrap

# Look for Sagan HIDS / Amun events - correlated events but not Snort events
#st_resultsSagan = os.stat(filenameSagan)
#st_sizeSagan    = st_resultsSagan[6]
#fileSagan.seek(st_sizeSagan)
#print "system     : Seek to end of " + filenameSagan

# Look for Snort events using internal IDS
st_resultsSnort = os.stat(filenameSnort)
st_sizeSnort    = st_resultsSnort[6]
fileSnort.seek(st_sizeSnort)
print "system     : Seek to end of " + filenameSnort

# Look for @netmenaces events
st_resultsNetmenaces = os.stat(filenameNetmenaces)
st_sizeNetmenaces    = st_resultsNetmenaces[6]
fileNetmenaces.seek(st_sizeNetmenaces)
print "system     : Seek to end of " + filenameNetmenaces

# Look for @evilafoot events
st_resultsEvilafoot = os.stat(filenameEvilafoot)
st_sizeEvilafoot    = st_resultsEvilafoot[6]
fileEvilafoot.seek(st_sizeEvilafoot)
print "system     : Seek to end of " + filenameEvilafoot

# Look for Suricata events
st_resultsSur = os.stat(filenameSur)
st_sizeSur    = st_resultsSur[6]
fileSur.seek(st_sizeSur)
print "system     : Seek to end of " + filenameSur

# Look for Shadow Snort events
st_resultsShadowSnort = os.stat(filenameShadowSnort)
st_sizeShadowSnort    = st_resultsShadowSnort[6]
fileShadowSnort.seek(st_sizeShadowSnort)
print "system     : Seek to end of " + filenameShadowSnort

# Look for Spade Snort events
st_resultsSpadeSnort = os.stat(filenameSpadeSnort)
st_sizeSpadeSnort    = st_resultsSpadeSnort[6]
fileSpadeSnort.seek(st_sizeSpadeSnort)
print "system     : Seek to end of " + filenameSpadeSnort

# Look for Fwsnort events
st_resultsFwSnort = os.stat(filenameFwSnort)
st_sizeFwSnort    = st_resultsFwSnort[6]
fileFwSnort.seek(st_sizeFwSnort)
print "system     : Seek to end of " + filenameFwSnort

# Look for Honeyd events
st_resultsHoneyd = os.stat(filenameHoneyd)
st_sizeHoneyd    = st_resultsHoneyd[6]
fileHoneyd.seek(st_sizeHoneyd)
print "system     : Seek to end of " + filenameHoneyd

# Look for Netflow events
st_resultsNetflow = os.stat(filenameNetflow)
st_sizeNetflow    = st_resultsNetflow[6]
fileNetflow.seek(st_sizeNetflow)
print "system     : Seek to end of " + filenameNetflow

# Look for Defcon events generated by sec
st_resultsDefcon = os.stat(filenameDefcon)
st_sizeDefcon    = st_resultsDefcon[6]
fileDefcon.seek(st_sizeDefcon)
print "system     : Seek to end of " + filenameDefcon

# Look for interesting events in Bro connection log
#st_resultsBroCon = os.stat(filenameBroCon)
#st_sizeBroCon    = st_resultsBroCon[6]
#fileBroCon.seek(st_sizeBroCon)
#print "system     : Seek to end of " + filenameBroCon

# Look for interesting events in honeyrtr AAA authentication log
st_resultsAuth = os.stat(filenameAuth)
st_sizeAuth    = st_resultsAuth[6]
fileAuth.seek(st_sizeAuth)
print "system     : Seek to end of " + filenameAuth

# Look for interesting events in honeyrtr AAA accounting log
st_resultsAcct = os.stat(filenameAcct)
st_sizeAcct    = st_resultsAcct[6]
fileAcct.seek(st_sizeAcct)
print "system     : Seek to end of " + filenameAcct

# Look for interesting events in p0f log
st_resultsp0f = os.stat(filenamep0f)
st_sizep0f    = st_resultsp0f[6]
filep0f.seek(st_sizep0f)
print "system     : Seek to end of " + filenamep0f

# Look for interesting events in Kojoney guru log
#st_resultsguru = os.stat(filenameguru)
#st_sizeguru    = st_resultsguru[6]
#fileguru.seek(st_sizeguru)
#print "system     : Seek to end of " + filenameguru

# Look for interesting events in honey router syslog
st_resultsrouter = os.stat(filenamerouter)
st_sizerouter    = st_resultsrouter[6]
filerouter.seek(st_sizerouter)
print "system     : Seek to end of " + filenamerouter

# Look for interesting events in honey router (IPv6) syslog
st_resultsrouterv6 = os.stat(filenamerouterv6)
st_sizerouterv6    = st_resultsrouterv6[6]
filerouterv6.seek(st_sizerouterv6)
print "system     : Seek to end of " + filenamerouterv6

# Look for interesting events in Conpot SCADA honepot syslog
st_resultsConpot = os.stat(filenameConpot)
st_sizeConpot    = st_resultsConpot[6]
fileConpot.seek(st_sizeConpot)
print "system     : Seek to end of " + filenameConpot

print " "
print "Waiting..."

# TransactionId - make this serialised and permanent at some point - BUG
txnId = -1

while True:
    
    try :    
        txnId = txnId + 1
        if txnId >= 1000000000 :
            txnId = 0
        # Sebek       
        #where = file.tell()
        #line  = file.readline()
    
        # syslogs from Honeypot itself -> keystrokes and wget
        #whereMessages = fileMessages.tell()
        #lineMessages  = fileMessages.readline()
    
        # Ossec
        whereOssec = fileOssec.tell()
        lineOssec  = fileOssec.readline()
    
        # Kippo
        whereKippo = fileKippo.tell()
        lineKippo  = fileKippo.readline()
        
        # TSOM
        whereTSOM  = fileTSOM.tell()
        lineTSOM   = fileTSOM.readline()
    
        # Telnet
        whereTelnet = fileTelnet.tell()
        lineTelnet  = fileTelnet.readline()
    
        # Clamd
        whereClamd = fileClamd.tell()
        lineClamd  = fileClamd.readline()
    
        # Spam
        whereSpam = fileSpam.tell()
        lineSpam  = fileSpam.readline()
    
        # Amun - submissions
        whereAmunSubmit = fileAmunSubmit.tell()
        lineAmunSubmit  = fileAmunSubmit.readline()
    
        # Amun - exploits
        whereAmunExploit = fileAmunExploit.tell()
        lineAmunExploit  = fileAmunExploit.readline()
    
        # Amun - downloads
        whereAmunDownload = fileAmunDownload.tell()
        lineAmunDownload  = fileAmunDownload.readline()
    
        # Glastopf
        whereGlastopf = fileGlastopf.tell()
        lineGlastopf  = fileGlastopf.readline()
    
        # PADS
        wherePads = filePads.tell()
        linePads  = filePads.readline()
        
        # PASSER
        wherePasser = filePasser.tell()
        linePasser  = filePasser.readline()
    
        # IPLOG
        whereIplog  = fileIplog.tell()
        lineIplog   = fileIplog.readline()
    
        # LMD
        whereMaldet  = fileMaldet.tell()
        lineMaldet   = fileMaldet.readline()
    
        # Honeytrap
        whereHoneytrap  = fileHoneytrap.tell()
        lineHoneytrap   = fileHoneytrap.readline()
    
        # Sagan
        #whereSagan = fileSagan.tell()
        #lineSagan  = fileSagan.readline()
    
        # @netmenaces
        whereNetmenaces = fileNetmenaces.tell()
        lineNetmenaces  = fileNetmenaces.readline()
    
        # @evilafootnet
        whereEvilafoot = fileEvilafoot.tell()
        lineEvilafoot  = fileEvilafoot.readline()
        
        # Snort - Internal : IN USE
        whereSnort = fileSnort.tell()
        lineSnort  = fileSnort.readline()
    
        # Suricata - Snort engine replacement : NOT IN USE
        whereSur = fileSur.tell()
        lineSur  = fileSur.readline()
        
        # Shadow Snort - external Snort-based IDS
        whereShadowSnort = fileShadowSnort.tell()
        lineShadowSnort  = fileShadowSnort.readline()
        
        # Spade Snort - external Snort-based ADS
        whereSpadeSnort = fileSpadeSnort.tell()
        lineSpadeSnort  = fileSpadeSnort.readline()
        
        # Fwsnort - internal IPS/IDS
        whereFwSnort = fileFwSnort.tell()
        lineFwSnort  = fileFwSnort.readline()
        
        # Honeyd
        whereHoneyd = fileHoneyd.tell()
        lineHoneyd  = fileHoneyd.readline()
    
        # Argus
        whereArgus = fileArgus.tell()
        lineArgus  = fileArgus.readline()
    
        # Bro 
        #whereBroCon = fileBroCon.tell()
        #lineBroCon  = fileBroCon.readline()
        
        # Router AAA Authentication 
        whereAuth   = fileAuth.tell()
        lineAuth    = fileAuth.readline()
    
        # Router AAA Accounting 
        whereAcct   = fileAcct.tell()
        lineAcct    = fileAcct.readline()
    
        # p0f 
        wherep0f   = filep0f.tell()
        linep0f    = filep0f.readline()
        
        # Guru 
        #whereguru  = fileguru.tell()
        #lineguru   = fileguru.readline()
    
        # Honey Router syslogs 
        whererouter  = filerouter.tell()
        linerouter   = filerouter.readline()
    
        # Honey Router (IPv6) syslogs 
        whererouterv6  = filerouterv6.tell()
        linerouterv6   = filerouterv6.readline()
    
        # Conpot syslogs 
        whereConpot    = fileConpot.tell()
        lineConpot     = fileConpot.readline()
    
        # Netflow
        whereNetflow = fileNetflow.tell()
        lineNetflow  = fileNetflow.readline()
    
        # Defcon
        #whereDefcon = fileDefcon.tell()
        #lineDefcon  = fileDefcon.readline()
        
        #if not lineMessages:		# no data in feed
            #print "nothing in Honeypot syslogs to process"
        #    fileMessages.seek(whereMessages)
        #else :			# new data has been added to log file
        #    print "*** NEW EVENT in Honeypot syslogs to process !"
            ###processChannelTweet(line) - very old - do not use
            ###processVisualisationTweet(line) - too verbose - add another twitter account to handle this feed
        #    processMessages(lineMessages)
        #    processSecure(lineMessages)
        #    processKeystrokes(lineMessages)
    
        if not lineAmunSubmit:		# no data in feed
            #print "nothing in Amun submissions.log file to process"
            fileAmunSubmit.seek(whereAmunSubmit)
        else :			# new data has been added to log file
            print "*** NEW EVENT in Amun submissions file to process !"
            tweet = kojoney_amun_parse.processAmunSubmit(lineAmunSubmit)
            if tweet != None :
                twitter_funcs.addTweetToQueue(tweet,geoip=False)
    
        if not lineAmunExploit:		# no data in feed
            #print "nothing in Amun exploit file to process"
            fileAmunExploit.seek(whereAmunExploit)
        else :			# new data has been added to log file
            print "*** NEW EVENT in Amun exploit file to process !"
            tweet = kojoney_amun_parse.processAmunExploit(lineAmunExploit)
            if tweet != None :
                twitter_funcs.addTweetToQueue(tweet,geoip=True)      
        
        if not lineClamd:		# no data in feed
            #print "nothing in Clamd log file to process"
            fileClamd.seek(whereClamd)
        else :			# new data has been added to log file
            print "*** NEW EVENT in Clamd log file to process !"
            tweet = kojoney_clamd_parse.processClamd(lineClamd,sensorId,txnId)
            if tweet != None :
                twitter_funcs.addTweetToQueue(tweet,geoip=True)      
            
        if not lineAmunDownload:		# no data in feed
            #print "nothing in Amun download file to process"
            fileAmunDownload.seek(whereAmunDownload)
        else :			# new data has been added to log file
            print "*** NEW EVENT in Amun download file to process !"
            tweet = kojoney_amun_parse.processAmunDownload(lineAmunDownload)
            if tweet != None :
                twitter_funcs.addTweetToQueue(tweet,geoip=True)
        
        #if not lineBroCon:		# no data in feed
        #    #print "nothing in Bro connection log file to process"
        #    fileBroCon.seek(whereBroCon)
        #else :			# new data has been added to log file
        #    #print "*** NEW EVENT in Bro connection log file to process !"
        #    tweet = kojoney_bro_parse.processBroCon(lineBroCon)
        #    if tweet != None :
        #        twitter_funcs.addTweetToQueue(tweet,geoip=True)
                
        # Glastopf - Web Honeypot     
        if not lineGlastopf:		# no data in feed
            #print "nothing in Glastopf log to process"
            fileGlastopf.seek(whereGlastopf)
        else :			# new data has been added to log file
            print "*** NEW EVENT in Glastopf log to process !"
            tweet = kojoney_glastopf_parse.processGlastopf(txnId,sensorId,lineGlastopf)
            if tweet != None :
                twitter_funcs.addTweetToQueue(tweet,geoip=True)
        
        # PADS - service discovery     
        if not linePads:		# no data in feed
            #print "nothing in PADS log to process"
            filePads.seek(wherePads)
        else :			# new data has been added to log file
            #print "*** NEW EVENT in PADS log to process !"
            tweets = kojoney_pads_parse.processPads(linePads)
            if tweets != None and len(tweets) != 0 :
                for tweet in tweets :
                    twitter_funcs.addTweetToQueue(tweet,geoip=True)
      
        # PASSER - service/banner discovery     
        if not linePasser:		# no data in feed
            #print "nothing in PASSER log to process"
            filePasser.seek(wherePasser)
        else :			# new data has been added to log file
            print "*** NEW EVENT in PASSER log to process !"
            tweet = kojoney_passer_parse.processPasser(linePasser)
            if tweet != None :
                twitter_funcs.addTweetToQueue(tweet,geoip=True)
        
        # IPLOG - scan/flood detection     
        if not lineIplog:		# no data in feed
            #print "nothing in IPLOG log to process"
            fileIplog.seek(whereIplog)
        else :			# new data has been added to log file
            #print "*** NEW EVENT in IPLOG log to process !"
            tweets = kojoney_iplog_parse.processIplog(txnId,sensorId,lineIplog)	# return multiple Tweets
            if tweets != None and len(tweets) != 0 :
                for tweet in tweets :
                    twitter_funcs.addTweetToQueue(tweet,geoip=True)
        
        # LMD - malware detection     
        if not lineMaldet:		# no data in feed
            #print "nothing in Maldet log to process"
            fileMaldet.seek(whereMaldet)
        else :			# new data has been added to log file
            #print "*** NEW EVENT in Maldet log to process !"
            tweet = kojoney_maldet_parse.processMaldet(txnId,sensorId,lineMaldet)
            if tweet != None :
                twitter_funcs.addTweetToQueue(tweet,geoip=False)
        
        # Spamholed - SPAM detection     
        if not lineSpam:		# no data in feed
            #print "nothing in Spamholed log to process"
            fileSpam.seek(whereSpam)
        else :			# new data has been added to log file
            print "*** NEW EVENT in SPAM log to process !"
            print lineSpam
            tweets = kojoney_spamhole_parse.processSpamholed(lineSpam)
            #if tweets != None and len(tweets) != 0 :
            #    for tweet in tweets :
            #        twitter_funcs.addTweetToQueue(tweet,geoip=True)

        # Argus - outgoing session detection     
        if not lineArgus:		# no data in feed
            #print "nothing in Argus log to process"
            fileArgus.seek(whereArgus)
        else :			# new data has been added to log file
            print "*** NEW EVENT in Argus log to process !"
            tweets = kojoney_argus_parse.processArgus(txnId,sensorId,lineArgus)	# return multiple Tweets
            if tweets != None and len(tweets) != 0 :
                for tweet in tweets :
                    twitter_funcs.addTweetToQueue(tweet,geoip=True)

        # honeytrap - similar to honeyd     
        if not lineHoneytrap :		# no data in feed
            #print "nothing in Honeytrap log to process"
            fileHoneytrap.seek(whereHoneytrap)
        else :			# new data has been added to log file
            print "*** NEW EVENT in Honeytrap log to process !"
            tweet = kojoney_honeytrap_parse.processHoneytrap(txnId,sensorId,lineHoneytrap)
            if tweet != None :
                twitter_funcs.addTweetToQueue(tweet,geoip=True)
        
        # Router AAA authentication attempts     
        if not lineAuth:		# no data in feed
            #print "nothing in AAA auth log to process"
            fileAuth.seek(whereAuth)
        else :			# new data has been added to log file
            print "*** NEW EVENT in Honey Router AAA Authentication log to process !"
            tweet = kojoney_aaa_parse.processAuth(lineAuth)
            if tweet != None :
                twitter_funcs.addTweetToQueue(tweet,geoip=True)
        
        # Router AAA accounting     
        if not lineAcct:		# no data in feed
            #print "nothing in AAA auth log to process"
            fileAcct.seek(whereAcct)
        else :			# new data has been added to log file
            print "*** NEW EVENT in Honey Router AAA Accounting log to process !"
            tweet = kojoney_aaa_parse.processAcct(lineAcct)
            if tweet != None :
                twitter_funcs.addTweetToQueue(tweet,geoip=True)

        # p0f     
        if not linep0f:		# no data in feed
            #print "nothing in p0f log to process"
            filep0f.seek(wherep0f)
        else :			# new data has been added to p0f log file
            #print "*** NEW EVENT in p0f log to process !"
            tweet = kojoney_p0f_parse.processp0f(linep0f)
            if tweet != None :
                twitter_funcs.addTweetToQueue(tweet,geoip=True)
        
        # Guru     
        #if not lineguru:		# no data in feed
        #    #print "nothing in guru log to process"
        #    fileguru.seek(whereguru)
        #else :			# new data has been added to guru log file
        #    print "*** NEW EVENT in guru log to process !"
        #    tweet = kojoney_guru_parse.processguru(lineguru)
        #    if tweet != None :
        #        twitter_funcs.addTweetToQueue(tweet,geoip=True)
        
        # Honey Router IPv4     
        if not linerouter:		# no data in feed
            #print "nothing in router syslog to process"
            filerouter.seek(whererouter)
        else :			# new data has been added to router syslog file
            print "*** NEW EVENT in Router honeypot (IPv4) syslog to process !"
            tweet = kojoney_router_parse.processrouter(linerouter)
            if tweet != None :
                twitter_funcs.addTweetToQueue(tweet,geoip=True)
        
        # Honey Router IPv6     
        if not linerouterv6:		# no data in feed
            #print "nothing in router syslog to process"
            filerouterv6.seek(whererouterv6)
        else :			# new data has been added to router syslog file
            print "*** NEW EVENT in Router honeypot (IPv6) syslog to process !"
            tweet = kojoney_router_parse.processrouterv6(linerouterv6)
            
            if tweet != None :
                twitter_funcs.addTweetToQueue(tweet,geoip=True)
        
        # Conpot     
        if not lineConpot:		# no data in feed
            #print "nothing in Conpot syslog to process"
            fileConpot.seek(whereConpot)
        else :			# new data has been added to router syslog file
            print "*** NEW EVENT in Conpot SCADA honeypot syslog to process !"
            tweet = kojoney_conpot_parse.processConpot(lineConpot)
            
            if tweet != None :
                twitter_funcs.addTweetToQueue(tweet,geoip=True)
            
        # OSSEC    
        if not lineOssec:		# no data in feed
        #    print "nothing in Ossec feed to process"
            fileOssec.seek(whereOssec)
        else :			# new data has been added to log file
            print "*** NEW EVENT in Ossec file to process !"
            tweet = kojoney_ossec_parse.processOssecSyslog(txnId,sensorId,lineOssec)
        
        # Add the GeoIP bit when this is working
        #if not lineSagan:		# no data in feed
            #print "nothing in Sagan event feed to process"
        #    fileSagan.seek(whereSagan)
        #else :			# new data has been added to log file
        #    print "*** NEW EVENT in Sagan alert file to process !"
        #    tweet = processSagan(lineSagan)
        #    if tweet != None:	# not every line in Sagan is required to be tweeted
        #        sendTweet(tweet)
        
        
        # Not needed if an external IDS is also being used
        if not lineSnort:		# no data in feed
        #    #print "nothing in Snort event feed to process"
            fileSnort.seek(whereSnort)
        else :			# new data has been added to log file
            print "*** NEW EVENT in Snort alert file (Internal IDS) to process !"
            tweet = kojoney_shadow_snort_parse.processSnortSyslog(lineSnort)
            if tweet != None:	# not every line in Snort is required to be tweeted
                twitter_funcs.addTweetToQueue(tweet,geoip=True)
        
        if not lineSur:		# no data in feed
            #print "nothing in Snort event feed to process"
            fileSur.seek(whereSur)
        else :			# new data has been added to log file
            print "*** NEW EVENT in Suricata IDS alert file to process !"
            tweet = kojoney_suricata_parse.processSur(lineSur)
            if tweet != None:	# 	not every line in Snort is required to be tweeted
                twitter_funcs.addTweetToQueue(tweet,geoip=True)
        
        if not lineShadowSnort:		# no data in feed
            #print "nothing in Shadow Snort event feed to process"
            fileShadowSnort.seek(whereShadowSnort)
        else :			# new data has been added to log file
            print "*** NEW EVENT in Shadow Snort IDS (External IDS) alert file to process !"
            tweet = kojoney_shadow_snort_parse.processSnortSyslog(lineShadowSnort)
            if tweet != None:	# 	not every line in Shadow Snort is required to be tweeted
                twitter_funcs.addTweetToQueue(tweet,geoip=True)
        
        if not lineSpadeSnort:		# no data in feed
            #print "nothing in Spade Snort event feed to process"
            fileSpadeSnort.seek(whereSpadeSnort)
        else :			# new data has been added to log file
            print "*** NEW EVENT in Spade Snort ADS (External ADS) alert file to process !"
            tweet = kojoney_spade_parse.processSpadeSyslog(lineSpadeSnort)
            if tweet != None:	# 	not every line in Spade Snort is required to be tweeted
                twitter_funcs.addTweetToQueue(tweet,geoip=True)
        
        if not lineNetmenaces :		# no data in feed
            #print "nothing in Netmenaces event feed to process"
            fileNetmenaces.seek(whereNetmenaces)
        else :			# new data has been added to log file
            print "*** NEW EVENT in @netmenaces (External Twitter Honeypot) alert file to process for IDMEF !"
            kojoney_netmenaces_idmef.sendNetmenacesIDMEF(lineNetmenaces)
        
        if not lineEvilafoot :		# no data in feed
            #print "nothing in Evilafoot event feed to process"
            fileEvilafoot.seek(whereEvilafoot)
        else :			# new data has been added to log file
            print "*** NEW EVENT in @evilafoot (External Twitter Honeypot) alert file to process for IDMEF !"
            kojoney_netmenaces_idmef.sendEvilafootIDMEF(lineEvilafoot)
            
        if not lineFwSnort:		# no data in feed
            #print "nothing in Fwsnort event feed to process"
            fileFwSnort.seek(whereFwSnort)
        else :			# new data has been added to log file
            print "*** NEW EVENT in Fwsnort IDS alert file to process !"
            #tweet = kojoney_fwsnort_parse.processFwSnortSyslog(lineFwSnort)
            #if tweet != None:	# 	not every line in Fwsnort is required to be tweeted
            #    twitter_funcs.addTweetToQueue(tweet,geoip=True)
            
            # get code ready to handle multiple tweets from brute force snorts
            tweets = kojoney_fwsnort_parse.processFwSnortSyslog(lineFwSnort)
            if tweets != None and len(tweets) != 0 :	# 	not every line in Fwsnort is required to be tweeted
                for tweet in tweets :
                    twitter_funcs.addTweetToQueue(tweet,geoip=True)
        
        if not lineKippo:		# no data in feed
            #print "nothing in Kippo event feed to process"
            fileKippo.seek(whereKippo)
        else :			# 	new data has been added to log file
            print "*** NEW EVENT in Kippo log file to process !"
            tweet = kojoney_kippo_parse.processKippo(txnId,sensorId,lineKippo)
            if tweet != None:		# not every line in Kippo log file is required to be tweeted
                twitter_funcs.addTweetToQueue(tweet,geoip=True)

        # code works - just that THreat Report algorithm is a little complex at the moment so avoid sending in Tweets        
        #if not lineTSOM:		# no data in feed
        #    #print "nothing in TSOM event feed to process"
        #    fileTSOM.seek(whereTSOM)
        #else :			# 	new data has been added to log file
        #    print "*** NEW EVENT in TSOM log file to process !"
        #    tweet = kojoney_tsom_parse.processTSOM(txnId,sensorId,lineTSOM)
        #    if tweet != None:		# not every line in TSOM log file is required to be tweeted
        #        twitter_funcs.addTweetToQueue(tweet,geoip=True)
        
        if not lineTelnet:		# no data in feed
            #print "nothing in Telnet event feed to process"
            fileTelnet.seek(whereTelnet)
        else :			# 	new data has been added to log file
            print "*** NEW EVENT in Telnet log file to process !"
            tweet = kojoney_telnetd_parse.processTelnetd(txnId,sensorId,lineTelnet)
            if tweet != None:		# not every line in Telnet log file is required to be tweeted
                twitter_funcs.addTweetToQueue(tweet,geoip=True)
                
        if not lineHoneyd:		# no data in feed
            #print "nothing in Honeyd event feed to process"
            fileHoneyd.seek(whereHoneyd)
        else :				# new data has been added to log file
            print "*** NEW EVENT in Honeyd log file to process !"
            print lineHoneyd
            tweet,flowEvent = kojoney_honeyd_parse.processHoneyd(lineHoneyd)
            #print tweet
            #print flowEvent
            if tweet != None :		# not every line in Honeyd log file is required to be tweeted
                twitter_funcs.addTweetToQueue(tweet,geoip=True)
            if len(flowEvent) != 0 :
                print "Send event to BRX" + flowEvent.__str__()    
                kojoney_blackrain.sendEvent(flowEvent)			# send the event to BRX
      
        if not lineNetflow:		# no data in feed
            #print "nothing in Netflow event feed to process"
            fileNetflow.seek(whereNetflow)
        else :				# new data has been added to log file
            print "*** NEW EVENT in Netflow event file to process !"
            tweet,flowEvent = kojoney_netflow_parse.processNetflow(lineNetflow)
            
            # something broke on 1 or 2 december so dont tweet until fixed
            #if tweet != None:	# not every line in Snort is required to be tweeted
            #    twitter_funcs.addTweetToQueue(tweet,geoip=True)
         
            # Need to re-instate the BRX : fixme
            #if flowEvent != None :
            #    #print "Send event to BRX" + flowEvent.__str__()    
            #    kojoney_blackrain.sendEvent(flowEvent)			# send the event to BRX
            #else:
            #    print "Problem sending event to BRX"
        
        #if not lineDefcon:		# no data in feed
            #print "nothing inDefcon event feed to process"
        #    fileDefcon.seek(whereDefcon)
        #else :			# new data has been added to log file
        #    print "*** NEW EVENT in Defcon event file to process !"
        #    tweet = processDefcon(lineDefcon)
        #    if tweet != None:	# not every line in Snort is required to be tweeted
        #        sendGeoIPTweet(tweet)
            
        #print "sleeping..."
        # this can be a float for sub-second sleep    
        time.sleep(0.5)		# 0.2 second
    
    except Exception,e:
        syslog.syslog("kojoney_tweet.py : main() exception caught = " + `e`)
        sys.exit()              
                                             