#!/usr/bin/python

import time, os , syslog , urlparse , re 

import ipintellib	# RCH library - master on mars
import mailalert	# RCH library
import p0fcmd		# RCH library - master on mars
import rch_asn_funcs	# RCH library - master on mars

# Globals
CLInum=0		# number of lines of CLI processed
Version="1.0"		# added p0f v 3.0.0
SessionId = -1		# makemsg() needs this : obsolete code ?

ROUTER = "172.31.0.9"
HPOT   = "172.31.0.67"

# need this so program can be monitored by monit
# make this a library function
# duplicated with kojoney_tail.py
def makePidFile(name):
    pid = os.getpid()
    
    pidFilename = "/var/run/rchpids/" + name + ".pid"
    fp=open(pidFilename,'w')
    print >> fp,pid
    fp.close()            
    #print "pid is " + `pid`
    return pid	# returns None if failed
                        

# duplicated with kojoney_tail.py
# make generic by setting "Sent by Kojoney Honeypot" to a fn parameter - override
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


# visualise the Tweets
# add timestamp as last (unusable) field
# duplicate in kojoney_tail.py
def writeSecViz5(tweet):

    #print "entered writeSecViz5()"
    now = time.time()
    
    try:    
        fields=tweet.split(",")
        #print fields
        
        timeS       = fields[0]
        type        = fields[1]		# e.g. ids , flow , amun, aaa
        node        = fields[2]		# e.g. mars
        phase       = fields[3]		# 
                
        # Filter
        # Ignore Amun events - no IP address
        if type.find("amun") != -1 :		
            return
        
        # Ignore AAA events - no IP address
        #if type.find("aaa") != -1 :		
        #    return
        
        # Extract event dependent fields
        srcIP       = fields[7]
        dstIP       = fields[10]
        event       = fields[12]		# e.g. full Snort message i.e. "[1:2323232:4] sdklsdklsdklsdk"
        countryCode = fields[4]
        ASname      = fields[5]
        dstPort     = fields[11]
        proto       = fields[9]
        
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
            proto = 'I' 
        
        # Compress Snort message down to purely the SID
        # How do I know the source of the SID i.e ET or standard Snort ?        
        if type == "ids":
            a = event.lstrip(" ")
            a = event.rstrip(" ")
            b = a.split(' ')[0]			# [1:232323:4]
            #print "b is " + `b`
            c = b.split(":")			# '[' , '232323' , '4' , ']'
            #print "c is " + `c`
            detail = c[1]			# 232323
            #print "detail is " + `detail`
            if event.find("ET ") != -1:		# Append "ET" if Emerging Threats signature
                detail = detail + "@ET"
        else:
            detail = event
            
        # Remove aaA redundant characters    
        detail=detail.replace(" cmd=","") 
        detail=detail.replace(" <cr>",":") 

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
        if type.find("fwall") != -1 :
            type = "FW" 
        if type.find("Aaa") != -1 :
            type = "AAU"
        if type.find("aaA") != -1 :
            type = "AAC" 
        if type.find("amun") != -1 :
            type = "AM" 
        if type.find("acl") != -1 :
            type = "ACL" 
                
        # For flow-derived events, construct the secviz file output fields[0-2] + additional info     
        msg = srcIP + "," + type + ":" + node + ":" + phase + ":" + detail + proto + dstPort + "," + dstIP + ",time=" + timeS + ",countryCode=" + countryCode + ",ASname=" + ASname + ",event=" + event
        
        # Do not visualise return flows - this needs to be done using proper correlation in next version
        # Needs more thought
        #if int(dstPort) < 1024 and srcIP == "HPOT" :
        #    syslog.syslog("writeSecviz5() discarded return flow : " + msg)  
        
        # Compress sources
        msg=msg.replace("bg_rtr","B")		# BG Router
        msg=msg.replace("node9","R")		# Honeypot Router
        msg=msg.replace("mars_fp","H")		# Honeypot
        msg=msg.replace("mars","H")		# Honeypot - fwsnort
        msg=msg.replace("adsl","A")		# WRT ADSL router
        
        
        # Misc compression
        msg=msg.replace("FEED:netflow","")
        msg=msg.replace("FEED:iptables","")
        msg=msg.replace("cli:router:","")
        msg=msg.replace('T22/23',"")
        msg=msg.replace("ACL:router:EVENT:","")
        
        msg=msg.replace("p0f:H:FEED:OS=","")
        msg=msg.replace("WW:H:FEED:File does not exist: ","")
          
        #print "WriteSecViz5(): " + msg
        
        # file needs to be touched
        fpOut = open(r'/home/var/log/kojoney_tail_secviz5_tweets.csv','a')
        print >> fpOut,msg 
        fpOut.close()

    except Exception,e:
        syslog.syslog("kojoney_tail.py : writeSecViz5() exception caught = " + `e` + " tweet=" + tweet)

# master in kojoney_tail.py
# wrapper for sending Tweets
def sendTweet(tweet_raw):
    global TweetClient
    
    MAXTWEET_LEN=139			# max chars to send
    
    now = time.time()
    
    #print "sendTweet(): raw = " + tweet_raw
    
    try:
        # Anonymise and shorten actual honeypot IP address to HPOT
        tweet = tweet_raw.replace("172.31.0.67","HPOT")        
        tweet = tweet_raw.replace("192.168.1.9","ROUTER")        
                
        # Try to shorten longer words in Snort messages
        tweet = tweet.replace("Classification: ","C:") 
        tweet = tweet.replace("Priority: ","P:") 
        tweet = tweet.replace("Administrator","Admin") 
        tweet = tweet.replace("Shellcode","SC") 
        tweet = tweet.replace("Windows Source","Win")
        tweet = tweet.replace("Information","Info")
        tweet = tweet.replace("{TCP}","{T}")
        tweet = tweet.replace("{ICMP}","{I}")
        tweet = tweet.replace("{UDP}","{U}")
        tweet = tweet.replace("(portscan) ","")
        tweet = tweet.replace("Executable ","Exe ")
        tweet = tweet.replace("Privilege ","Priv ")
        tweet = tweet.replace("ATTACK_RESPONSE","ATT_RESP")
        tweet = tweet.replace("ATTACK-RESPONSES","ATT_RESP")
        tweet = tweet.replace("Microsoft","M$oft")		# personal spite
        tweet = tweet.replace("MS ","M$oft ")			# personal spite
        tweet = tweet.replace("symantec","Symantec")		# grammar
        tweet = tweet.replace("Unauthenticated","Unauth")
        tweet = tweet.replace("antivirus","AV")
        tweet = tweet.replace("download","dload")
        tweet = tweet.replace("CMD Shell","cmd.exe")		# consistency
        tweet = tweet.replace("Attempted","Attempt")
        tweet = tweet.replace("NETBIOS","NBIOS")
        tweet = tweet.replace("version","ver")
        tweet = tweet.replace("Request","req")
        tweet = tweet.replace("overflow","oflow")
        tweet = tweet.replace("xor","XOR")
        tweet = tweet.replace("was detected","detected")
        tweet = tweet.replace("crouchr","****")			# AAA logs for router login
         
        # construct and prepend a minimal localtime timestamp : HHMM   
        tuple=time.localtime(now)
        timestamp = "%02d" % tuple.tm_hour + "%02d" % tuple.tm_min    
        tweet = timestamp + "," + tweet
    
        # truncate (concatenate in future ?) long tweets 
        if len(tweet) >= MAXTWEET_LEN:
            tweet=tweet[0:MAXTWEET_LEN]
            tweet=tweet + "+"				# + indicates tweet was truncated
            syslog.syslog("kojoney_tail.py : sendTweet() msg built [truncated to " + `len(tweet)` + " chars] : tweet=" + tweet)
        else:     
            syslog.syslog("kojoney_tail.py : sendTweet() msg built : " + tweet)
            
        # basic visualisation of the Tweets
        writeSecViz5(tweet)
        
        # hack - do not Tweet firewall and netflow basic feeds
        if tweet_raw.find("FEED") != -1 :
            return
    
        # actually send the tweet
        status = TweetClient.PostUpdate(tweet)    
        print "notify     : Tweet sent : " + tweet
        syslog.syslog("kojoney_tail.py : sendTweet() Tweet sent : " + tweet)
            
        # log the sent Tweets - have a .txt extension so Windoze can open it up
        fpOut = open(r'/home/var/log/tweets.log.txt','a')
        print >> fpOut,"TWEET=" + tweet 
        fpOut.close()

        # send an e-mail if the exploit contains particularly interesting keywords
        if tweet.find("Cisco") != -1 or tweet.find("Conficker") != -1 or tweet.find("Downadup") != -1 :
            statusAlert("Exploit du jour detected",tweet)
        
        # send an e-mail if router command-line is being entered
        if tweet.find("@RTR") != -1 :
            statusAlert("Router honeypot being accessed",tweet)
        
        time.sleep(1)					# crude rate limit 
    
    except Exception,e:
        syslog.syslog("kojoney_tail.py : sendTweet() exception caught = " + `e` + " tweet=" + tweet)

# main routine for writing to kojoney Channel        
# master in kojoney_tail.py
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

    
    
# extract source IP from Snort log
# source IP can be either 1.2.3.4:80 or 1.2.3.4 (i.e. include a port number)
# make this a function and extend to extract srcip,srcport,dstIP,dstPort and return a dictionary
# master in kojoney_tail.py

def getSrcIPSnort(line):
    sock={}
    try:
        line=line.strip("\n")
        #print "getSrcIPSnort() : line is " + line.strip("\n")
        a=line.find("}")
    
        if a == -1:	# Failed to find '}'
            print "Failed to find } anchor"
            syslog.syslog("kojoney_tail.py : getSrcIPSnort() failed to find } anchor in " + line)
            sock['ip']   = "0.0.0.0"
            sock['port'] = "-1"
            return sock
        
        b = line[a:].strip("\n")
    
        #print "b=" + b
        c=b[2:]			# skip "{ "
        #print "c=[" + c +"]"
    
        d = c.split(" ")		# d = 1.2.3.4 or 1.2.3.4:345
        #print "d is " + `d`
    
        if d[0].find(":") != -1 :	# d = 1.2.3.4:80
            sock['ip']  = d[0].split(":")[0]
            sock['port'] = d[0].split(":")[1]
        else:				# TCP portscan is this type
            #print "getSrcIPSnort() IP without port number found d=" + d
            sock['ip']   = d[0]
            sock['port'] = "-1"
            
        #print "getSrcIPSnort() : ip is [" + sock['ip'] + "] and port is [" + sock['port'] + "]"
    
        return sock
    
    except Exception,e:
        syslog.syslog("kojoney_tail.py : getSrcIPSnort() exception caught = " + `e` + " line=" + line.strip("\n"))
        return None

# master in kojoney_tail.py
# extract destination IP from Snort log
# IP can be either 1.2.3.4:80 or 1.2.3.4
# make this a function and extend to extract srcip,srcport,dstIP,dstPort and return a dictionary
def getDstIPSnort(line):
    sock={}
    
    try:
        line=line.strip("\n")
        #print "getDstIPSnort() : line is " + line
        a=line.find("}")
    
        if a == -1:	# Failed to find '}'
            syslog.syslog("kojoney_tail.py : getDstIPSnort() failed to find } anchor in " + line)
            sock['ip']   = "0.0.0.0"
            sock['port'] = "-1"
            return sock
        
        b = line[a:].strip("\n")
    
        #print "b=" + b
        c=b[2:]				# skip "{ "
        #print "c=[" + c +"]"		# c = 1.2.3.4:80 -> 3.4.5.6:80
    
        d = c.split(" ")		# d = {'1.2.3.4', '->', '3.4.5.8'}
        #print "d is " + `d`
    
        if d[2].find(":") != -1 :	# d = 1.2.3.4:80
            sock['ip']   = d[2].split(":")[0]
            sock['port'] = d[2].split(":")[1]
        else:
            sock['ip']   = d[2]
            sock['port'] = "-1"
            
        #print "getDstIPSnort() : ip is [" + sock['ip'] + "] and port is [" + sock['port'] + "]"
    
        return sock
    
    except Exception,e:
        syslog.syslog("kojoney_tail.py : getDstIPSnort() exception caught = " + `e` + " line=" + line.strip("\n"))
        return None

# Request autoblock from PSAD
# just log the request for the moment
# add try:exception
def psadBlock(srcIP,reason) :
    cmd = "psad --fw-block-ip " + srcIP
    event = "kojoney_ar.py : PSAD auto-block requested for " + srcIP + ", reason=" + reason
    syslog.syslog(event)
    os.system(cmd)

# Process Snort log entries
# Look for initial reconnaisance
#vi.e. NMAP pings etc
# TODO : add Nmap scan but only if dest is 172.31.0.67:22
# TODO : dump never seen before messages to a text file
# todo : add writeSecViz4 for TCP-related events (i.e. can get an accurate uptime)
# create the phase from the snort message i.e look for EXPLOIT
# todo - reinstate the [x:SIG:Rev] for visualisation
# todo : use pattern matching to extract IPs and SID
# PSAD should then write an entry to psad syslog file
# psad syslog file processing code in kojoney_tail.py should then add the visualisation data

def processSnortAR(line):
    try:
        line=line.strip("\n")        
        print "snortAR    : " + line
        
        # Filter out non-Snort messages
        if line.find("last message repeated") != -1:
            return

        # Extract the Snort event message
        fields=line.split(' ')
        #print fields
        snortMsg = " ".join(fields[5:])		# skip Snort timestamp
        snortMsg = snortMsg.strip('\n');
                     
        # Extract flow information from Snort message             
        srcSock = getSrcIPSnort(line)
        dstSock = getDstIPSnort(line)             
        srcIP   = srcSock['ip']
        dstIP   = dstSock['ip']
        srcPort = srcSock['port']
        dstPort = dstSock['port']
        
        # Extract proto from Snort
        if line.find("{ICMP}")  != -1 :
            proto = "1"
        elif line.find("{TCP}") != -1 :
            proto = "6"
        elif line.find("{UDP}") != -1 :
            proto = "17"
        else :
            proto = "?"            
        
        # Do not report "attacks" against Twitter
        if dstIP.find("168.143.161.") != -1:
            return
        if dstIP.find("168.143.162.") != -1:
            return
        if dstIP.find("168.143.171.") != -1:
            return
            
        # Do not report "attacks" against Sandbox analysers
        if dstIP.find("128.121.146.") != -1:
            return

        # Do not report "attacks" from local LAN
        if srcIP.find("192.168.1.") != -1 or dstIP.find("192.168.1.") != -1 :
            return
            
        # Anonymise/compress honeypot IP address
        if srcIP == HPOT:
            srcIP   = "HPOT"
      
        if dstIP == HPOT:
            dstIP = "HPOT"
        
        # Anonymise/compress router IP address
        if srcIP == ROUTER:
            srcIP   = "ROUTER"
      
        if dstIP == ROUTER:
            dstIP = "ROUTER"
        
        #print "got to here"            
        flow = srcIP + ",(" + srcPort + "),[" + proto + "]," + dstIP + ",(" + dstPort + ")"               
        #flow = srcSock['ip'] + ",(" + srcSock['port'] + "),[" + proto + "]," + dstSock['ip'] + ",(" + dstSock['port'] + ")"               
        #print "processSnort() : line  is " + line.strip("\n")
        #print "processSnort() : flow  is " + flow

        # List of events for which AR should not be applied
        if line.find("ET POLICY Outbound TFTP ACK") != -1 :	# Malware downloads trigger many of these   
            return  

        # psad white-list should prevent this : SSH related SIDs that could lock me out of the mars box !!!
        if line.find("2001980") != -1 or line.find("2001984") != -1:
            syslog.syslog("kojoney_ar.py : do not block on SSH-related events : SID 2001980 or 2001984")
            return
        
        # This code is optimised for malware collector debugging
        # Brute force SSH sttampts can cause Afterglow reports to be sparse
        # List specific Snort events to cause AR to be triggered
        if line.find("2006546") != -1 :		# SSH brute force
            # todo : use snort Priority field to determine if to block or not ?    
            # unconditionally request PSAD to auto-block any (non-white listed) IP triggering a Snort IDS alert    
            #psadBlock(srcIP,"SnortIDS signature match")
            psadBlock(srcIP,"SID 2006546 : LibSSH brute-force attack")
        elif line.find("ET SCAN Rapid POP3 Connections") != -1:
            psadBlock(srcIP,"SID 2002992 : POP3 brute-force attack")     
        else :	# default is not to block attackers
            return 
           
    except Exception,e:
        syslog.syslog("kojoney_ar.py : processSnortAR() exception caught = " + `e` + "line=" + line)


# master in kojoney_tail.py
# 
def processPSAD(line):
    
    # default is recon - override based on the SID
    phase = "RECON"
    srcIP   = "-1"
    dstIP   = "-1"
    proto   = "IP"
    srcPort = "-1"
    dstPort = "-1"

    pat = r'\d+\.\d+\.\d+\.\d+'		# locate a number of IP addresses
        
    try:        
        line = line.strip('\n')
                
        # ignore if this is not a psad-originated syslog entry
        if line.find("psad") == -1:
            return
          
        #print "processPSAD() : line read from log file : " + line
        # locate IP addresses in the event
        ips = re.findall(pat,line)        
        #print ips
        
        # todo - parse relevent additional info e.g. source IP,etc to construct a flow     
        # some information is lost from the original message - fix this in later version
        if line.find("scan detected") != -1:
            srcIP = ips[0]
            dstIP = ips[1]
            event = line[27:]			# skip pre-amble : full message
            event = "scan"
            phase = "RECON"
        elif line.find("signature match:") != -1:
            event = line[27:]			# skip pre-amble
            phase = "RECON"
        elif line.find("added iptables auto-block") != -1:
            srcIP = ips[0]
            event = line[27:]			# skip pre-amble : full message
            event = "add-block:" + srcIP	# replace with a short version to make Tweet replaces easier : hack
            phase = "AR_ADD"			# Active Response : Added
        elif line.find("removed iptables auto-block") != -1:
            srcIP = ips[0]
            event = line[27:]			# skip pre-amble
            event = "del-block:" + srcIP
            phase = "AR_DEL"			# Active Response : Removed
        else:					
            return
                                 
        sensorName = "mars"			# hostname of sensor 
        
        # Anonymise/compress mars honeypot IP address 
        #if srcIP == HPOT :
        #    srcIP = "HPOT"
        #if dstIP == HPOT :
        #    dstIP = "HPOT"
      
        # Anonymise/compress router (node9) honeypot IP address
        #if srcIP == ROUTER:
        #    srcIP   = "ROUTER"
      
        #if dstIP == ROUTER:
        #    dstIP = "ROUTER"
        
        # This is the ideal where there is the proto number ?
        #if line.find("ICMP")  != -1 :
        #    proto = "1"
        #elif line.find("TCP") != -1 :
        #    proto = "6"
        #elif line.find("UDP") != -1 :
        #    proto = "17"
  
        # Ignore real destination IP to make the AfterGlow layout cluster PSAD events away from HPOT
        dstIP = "PSAD"
                      
        flow1 = srcIP + ",(" + srcPort + "),[" + proto + "]," + dstIP + ",(" + dstPort + ")"
        #flow2 = "ttl=" + ttl + ",ipid=" + ipid 
            
        # Construct the event message       
        msg = "psad" + "," + sensorName + "," + phase + "," + getIntelStr(srcIP,"-1") + "," + flow1 + "," + event 
        print "psad       : " + msg
        
        # Log to kojoney_tail.log    
        makeMsg(0,"0",msg)
        sendTweet(msg)		# hack to get secviz5() called
        
    except Exception,e:
        syslog.syslog("kojoney_tail.py : processPSAD() exception caught = " + `e` + "line=" + line)

# master in kojoney_tail.py
# add try: exception to this
# get intel on not the hpot IP 
def getIntelStr(ip1,ip2):
    
    ip = "0.0.0.0"
    #print "getintelStr() : ip1= " + ip1 + " ip2=" + ip2
    
    try: 
    
        if ip1 == ROUTER :
            ip = ip2
        if ip2 == ROUTER :
            ip = ip1    
        
        if ip1 == 'ROUTER' :
            ip = ip2
        if ip2 == 'ROUTER' :
            ip = ip1    
        
        if ip1 == 'HPOT' :
            ip = ip2
        if ip2 == 'HPOT' :
            ip = ip1    
        
        if ip1 == HPOT :
            ip = ip2
        if ip2 == HPOT :
            ip = ip1    
                
        #print "Called getIntelStr(): IP to be checked is " + ip
        
        if (ip == ROUTER or ip == HPOT or ip == "ROUTER" or ip == "HPOT") :
            intelStr = "*,*,*"		# * = masked
        else :
            # Handle 192.168.1.131 used for testing
            #if line.find("192.168.1.") != -1 :
        
            #if ip == "0.0.0.0" :		# failed to extract IP from a record
            #    return "intell=0.0.0.0"
    
            # Get DNS info
            dnsInfo = ipintellib.ip2name(ip)
            dnsName = dnsInfo['name']
        
            # WHOIS : primary information
            asInfo = rch_asn_funcs.ip2asn(ip)				# need to add routes=1 to get ASN - timeout bug at moment
            asNum = asInfo['as']					# AS123 
            asRegisteredCode = asInfo['registeredCode']			# Short-form e.g.ARCOR
            countryCode = asInfo['countryCode']
        
            # WHOIS info gathered from "infos" fields
            info        = asInfo['info']
            purpose     = asInfo['purpose']
            vodafone    = asInfo['vodafone']
        
            # GeoIP information
            #geoIP = ipintellib.geo_ip(ip)				# getting exceptions still !
            #countryCode = geoIP['countryCode']
            #city        = geoIP['city']
            #longitude   = geoIP['longitude']				# Used to calc approx. localtime
            
            #intelStr = countryCode + ":" + asNum + ":" + asRegisteredCode + ":" + city + ":" + dnsName 
            intelStr = countryCode + "," + asNum + "," + asRegisteredCode     
    
            # ,long=" + "%.2f" % float(longitude) 
            
        #print "***** intelStr for " + ip + " is " + intelStr 
        return intelStr        

    except Exception,e:
        syslog.syslog("kojoney_tail.py : getIntelStr() exception caught = " + `e` + "ip=" + ip)
        return "intell=exception!"
       
# ----------------------------------------------
        
# Start of code        
           
# Make pidfile so we can be monitored by monit        
pid =  makePidFile("kojoney_ar")
if pid == None:
    syslog.syslog("Failed to create pidfile for pid " + `pid`)
    sys.exit(0)
else:
    syslog.syslog("kojoney_tail started with pid " + `pid`)
                
# Send an email to say kojoney_tail has started
makeMsg(0,"0","system,kojoney_ar started with pid=" + `pid`)
a = "kojoney_ar started with pid=" + `pid`

statusAlert("*** kojoney_ar started",a)
    
# Set the Snort filename to scan
filenameSnort = '/home/var/log/snort.syslog'
fileSnort = open(filenameSnort,'r')


# ------------
# tail -f mode
# ------------

# Find the size of the Snort file and move to the end
st_results_snort = os.stat(filenameSnort)
st_size_snort = st_results_snort[6]
fileSnort.seek(st_size_snort)
print "system     : Seek to end of Snort IDS feed"

while True:
    
    # Snort
    whereSnort = fileSnort.tell()
    lineSnort  = fileSnort.readline()
            
    if not lineSnort:		# no data in snort.syslog
        #print "nothing in Snort logfile to process"
        fileSnort.seek(whereSnort)
    else:			# new data has been added to log file
        #print "*** NEW EVENT in Snort syslog to process !"
        processSnortAR(lineSnort)
    
    #print "sleeping..."    
    time.sleep(0.1)
                                                                            