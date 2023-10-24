#!/usr/bin/python

# Tail the Kojoney Channel and produce visualisation files

import sys, time, os , syslog , urlparse , re 
#import twitter		# Google API

import ipintellib	# RCH library - master on mars
import mailalert	# RCH library
import p0fcmd		# RCH library - master on mars
#import rch_asn_funcs	# RCH library - master on mars

import getSnortInfo	# RCH code - not a module

ROUTER = "172.31.0.9"
HPOT   = "172.31.0.67"
HONEYD = "172.31.0.1"

IBG    = "172.31.0.47"	# IP address sending netflow 

SeqNo = 0		# increment for each unique event found
#StartTime = time.time()	# Send out a report after 1 hour

MalwareMD5 = sys.argv[1]

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
        syslog.syslog("kojoney_viz.py : statusAlert() : " + `e`)


# Write Security Visualisation data to be processed by AfterGlow to .csv file
# Format : IP_address,commandStr
# Need to touch this file
# TODO : add boot time epoch hours to output file as a way of tracking commands entered by a single haxx0r
# This file can be parsed by awk scripts to format it suitable for visualisation

def writeSecViz1(ip,username,countryCode,commandStr):
    try:    
        #p0fInfo = p0fcmd.getP0fInfo(ip,"0","172.31.0.67","22");
        #if p0fInfo['result'] == True:
        #    p0fStr = "os:" + p0fInfo['genre'] + ":hops=" + p0fInfo['hops'] 
        #else:
        #    p0fStr = p0fInfo['errormsg']
        
        #raise Exception	# test code
        #print i		# force exception for testing
        
        #asInfo = rch_asn_funcs.ip2asn(ip)
        #asNum = asInfo['as']				        # AS123 
        #asRegisteredCode = asInfo['registeredCode']		# Short-form e.g.ARCOR
        
        # Get DNS info
        dnsInfo = ipintellib.ip2name(ip)
        dnsName = dnsInfo['name']
        
        # Get current time (GMT)
        nowGMT = time.gmtime(time.time())
        
        #msg = ip + ":" + asNum + ":" + asRegisteredCode + ":" + p0fStr + "," + username + "," + '"' + commandStr + '"' + "," + countryCode  
        msg = time.asctime(nowGMT) + "," + ip + "," + dnsName + "," + countryCode + "," + username + "," + '"' + commandStr + '"' 
        
        # Write to file
        fpOut = open(r'/home/var/log/kojoney_tail_secviz_cmds.csv','a')
        print "writeSecViz1():" + msg
        print >> fpOut,msg
        fpOut.close()
        
    except Exception,e:
        syslog.syslog("kojoney_tail.py : writeSecViz1() exception caught = " + `e` + " ip=" + ip)

# Write Security Visualisation data to be processed by AfterGlow to .csv file
# Format IP_address,commandStr
# Need to touch this file
# This file can be parsed by awk scripts to format it suitable for visualisation

def writeSecViz2(ip,username,countryCode,fileName):
    try:    
        #p0fInfo = p0fcmd.getP0fInfo(ip,"0","172.31.0.67","22");
        #if p0fInfo['result'] == True:
        #    p0fStr = "os:" + p0fInfo['genre'] + ":hops=" + p0fInfo['hops'] 
        #else:
        #    p0fStr = p0fInfo['errormsg']
        #
        #    asInfo = rch_asn_funcs.ip2asn(ip)
        #    asNum = asInfo['as']					# AS123 
        #    asRegisteredCode = asInfo['registeredCode']		# Short-form e.g.ARCOR
            
        # Get DNS info
        dnsInfo = ipintellib.ip2name(ip)
        dnsName = dnsInfo['name']
          
        # Get current time (GMT)
        nowGMT = time.gmtime(time.time())
            
        msg = time.asctime(nowGMT) + "," + ip + "," + dnsName + "," + countryCode + "," + '"' + filename + '"'
                        
        # Write to file
        fpOut = open(r'/home/var/log/kojoney_tail_secviz_dloads.csv','a')
        #msg = ip + ":" + asNum + ":" + asRegisteredCode + ":" + p0fStr + "," + username + "," + fileName + "," + countryCode
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
        
        #asInfo = rch_asn_funcs.ip2asn(ip)
        asInfo = ipintellib.ip2asn(ip)
        #asNum = asInfo['as']					# AS123 
        asRegisteredCode = asInfo['registeredCode']		# Short-form e.g.ARCOR
        
        msg = ip + "," + `bootTimeEpochHours` + "," + ip + ":" + Username + "," + "os=" + os + ",hops=" + hops + ","\
        + asRegisteredCode + ",now=" + nowStr + "," + `now` + ",bootTime=" + bootTimeStr + "," + `bte` + ",fw=" + fw + ",nat=" + nat
        
        print "WriteSecViz3() = " + msg
        
        fpOut = open(r'/home/var/log/kojoney_tail_secviz3_uptime.csv','a')
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
        
        #asInfo = rch_asn_funcs.ip2asn(ip)
        asInfo = ipintellib.ip2asn(ip)
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


UniqueEvent = {}
UniqueSid   = {}

# Read a line fom kojoney Channel and add to file if it is unique
def processChannelViz(line):
    #print "entered processChannelViz()"
    global UniqueEvent
    global UniqueSid
    global SeqNo
    
    try:
        msg="error"			# msg should be overwritten
        
        fields=line.split(",")
        #print "processChannelViz() : " + `fields`
        
        timeS       = fields[0]
        type        = fields[4]		# e.g. ids , flow , amun , aaa , honeyd
        node        = fields[5]		# e.g. mars
        phase       = fields[6]		# 
                
        # Filter
        # ignore incoming DTX-IN flows, they are just the return traffic from C&C servers
        if line.find("DTX-IN") != -1 :
            return
            
        if line.find("PROBE_C") != -1 :
            return
            
        # Extract event independent fields
        srcIP       = fields[14]
        dstIP       = fields[18]
        event       = fields[21]		# e.g. full Snort message i.e. "[1:2323232:4] sdklsdklsdklsdk"
        
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
        
        # Compress Event Type
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
        
        # For netflow records extract the egress interface and append it to the router name
        # Afterglow can match on "-if0" to show dropped flows
        if type == "FL" :
            #print "outIf:" + fields[30]
            outIf = fields[30].split("=")[1]
            #print "outIf=" + outIf
            node = node + "-if" + outIf
            
        # Has the event been seen before ? 
        ukey = srcIPinfo + "," + type + ":" + node + ":" + phase + ":" + event + ":" + proto + dstPort
        #print "ukey=" + ukey 
        
        if UniqueEvent.has_key(ukey) == False:
            UniqueEvent[ukey] = 1	# make this a timestamp ? epoch
            SeqNo = SeqNo + 1
            
            # For flow-derived events, construct the secviz file output fields[0-2] + additional info     
            addInfo = ",time=" + timeS + ",ASname=" + ASname + ",CC=" + countryCode + ",event=" + event + ",dns=" + dnsName + ",AScode=" + AScode
            msg = srcIPinfo + "," + "#" + `SeqNo` + " " + type + ":" + node + ":" + phase + ":" + event + ":" + proto + dstPort + "," + dstIPinfo + addInfo
        
            # Do not visualise return flows - this needs to be done using proper correlation in next version
            # Needs more thought
            #if int(dstPort) < 1024 and srcIP == "HPOT" :
            #    syslog.syslog("writeSecviz5() discarded return flow : " + msg)  
        
            # Compress sources - i.e. hostname of the node producing the record
            msg=msg.replace("bg_rtr","BG")		# BG Router
            msg=msg.replace("BG-","")		        # leave only "ifX"
            msg=msg.replace("node9","R")		# Honeypot Router
            msg=msg.replace("mars_fp","H")		# Honeypot
            msg=msg.replace("mars","H")		        # Honeypot - fwsnort
            msg=msg.replace("adsl","")	         	# WRT ADSL router
            #msg=msg.replace("fwall","WRT")		# WRT ADSL router is an iptables firewall
        
            # Misc compression
            msg=msg.replace("SYN:SYN","SYN")
            msg=msg.replace("DTX-OUT:DTX","DTX")
            msg=msg.replace("HPOT","DRONE_MALWARE_UNDER_TEST")	# force a nice wide text box in Afterglow
            msg=msg.replace("FL:","")
            msg=msg.replace("IDS:H:EXPLT:","")
            msg=msg.replace("IPS:H:EXPLT:","")
            msg=msg.replace("REI:HTTP_XFER","DTX")	# netflow
            msg=msg.replace(":EVENT:HTTP_XFER","DTX")	# firewall
            msg=msg.replace(":PING","")		# IRC
            msg=msg.replace(":PONG","")
            msg=msg.replace(":USERHOST","")
            msg=msg.replace(":FEED:iptables:","")
        
            # file is created when this process first runs
            print "unseen event -> add to dictionary and fingerprint file : " + msg
            fpOut = open(r'/home/var/log/kojoney_fprint.csv','a')
            print >> fpOut,msg 
            fpOut.close()

        # Create SID text graph : Has the SID been seen before ? if not, add to the graph tree with text version of message 
        if type == "IDS" and (line.find("EXPLT") != -1) :
            sid = event.split("=")[1]
            #print "IDS EXPLT event : SID is " + sid
            
            # bug ??? : what if the event is not a snort event but a fwsnort or psad event ?
            if UniqueSid.has_key(sid) == False:
                UniqueSid[sid] = 1	# make this a timestamp ? epoch
                #print "msg        = " + getSnortInfo.getSnortMsg(sid) 
                #print "classtype  = " + getSnortInfo.getSnortAtom(sid,"classtype")
                #print "reference  = " + getSnortInfo.getSnortAtom(sid,"reference")
                snortMsg = getSnortInfo.getSnortMsg(sid).replace("\"","")
                snortRef = getSnortInfo.getSnortAtom(sid,"reference").replace("\"","")
                #msg = "SID" + "," + sid + "," +  snortMsg + ":" + snortRef
                msg = "IDS_SID_KEY" + "," + "sid:" + sid + ",sid:" +  snortMsg
                
                # file is created when this process first runs
                print "unseen Snort event -> add to dictionary and fingerprint file"
                fpOut = open(r'/home/var/log/kojoney_fprint.csv','a')
                print >> fpOut,msg 
                fpOut.close()        
        
        # file needs to be touched - this will become obsolete
        #fpOut = open(r'/home/var/log/kojoney_tail_secviz5_tweets.csv','a')
        #print >> fpOut,msg 
        #fpOut.close()

    except Exception,e:
        syslog.syslog("kojoney_viz.py : processChannelViz() exception caught = " + `e` + " line=" + line)


# Process dns log from Malware hosting system DNSmasq sending syslog to /var/log/debug
# This data does not come from the Kojoney Channel file since it is not a flow type of event
UniqueDNS = {} 
DNStransaction = 0					# increment this to make each event unique for display by Afterglow
               
def processdns(line):   
    global UniqueDNS    
    global DNStransaction
    global SeqNo                                       
    try:                
        if line.find("dnsmasq[") != -1 :                                                                                                                                                                                                                                                                               
            #if line.find("NXDOMAIN-IPv4")    != -1:     # ignore No Name responses
            #    return
            #if line.find("NXDOMAIN-IPv6")    != -1:     # ignore No Name responses
            #    return
            #if line.find("NODATA-IPv6")      != -1:     # ignore No Name responses
            #    return            
            #if line.find("obmr.btconnect.com") != -1:   # ignore BT Connect e-mail
            #return
                                                                                                                                                                                                                                                                                                                                                                                                                                                   
            # Log interesting DNS replies    
            if line.find("reply") != -1 or line.find("cached") != -1:
                a = line.split(" ")
                name = a[6]
                ip   = a[8]
                #print "dns        : " + name + " resolved to " + ip
                                        
                # some PTR requests for 217.41.27.169 are being performed -> leave these out for the time being
                # code is not clever enough to differentiate between [PTR] and [A] responses                        
                if name.find("217.41.27.169") != -1 :
                    return                                                                                                        
                if ip.find("217.41.27.169") != -1 :
                    return                                                                                                        
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
                # has this name->IP pair been seen before ?
                #dnsPair = "RQ:" + name + ",DNS," + ip		# add "RQ:" so that DNS names can be identified and colour-coded in Afterglow
                dnsPair = name + "," + ip			# add "RQ:" so that DNS names can be identified and colour-coded in Afterglow
                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
                if UniqueDNS.has_key(dnsPair) == False :
                    DNStransaction = DNStransaction + 1
                    SeqNo = SeqNo + 1
                    geoIP = ipintellib.geo_ip(ip)
                    countryCode = geoIP['countryCode']
                    msg = "RQ:" + name + "," + "#" + `SeqNo` + " " + "DNS_" + `DNStransaction` + "," + ip + ":" + countryCode 
                    print "unique DNS pair found, add the following entry to visualisation file : " + msg
                    UniqueDNS[dnsPair] = 1	# change to now epoch ?
                    # log unique name -> IP mappings to a file for Afterglow post-processing - this file must have been touched
                    fpOut = open(r'/home/var/log/kojoney_fprint.csv','a')
                    print >> fpOut,msg
                    fpOut.close()
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
    except Exception,e:
        syslog.syslog("kojoney_viz.py : processdns() exception caught = " + `e` + "line=" + line)


def processSebek(line):   
    
    try:                
        pass
        #print "processSebek : " + line                                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
    except Exception,e:
        syslog.syslog("kojoney_viz.py : processSebek() exception caught = " + `e` + "line=" + line)
# -------------------------------------------------------
        
# Start of code        
        
       
# Make pidfile so we can be monitored by monit        
pid =  makePidFile("kojoney_viz")
if pid == None:
    syslog.syslog("Failed to create pidfile for pid " + `pid`)
    sys.exit(0)
else:
    syslog.syslog("kojoney_viz started with pid " + `pid`)
                
# Send an email to say kojoney_tail has started
now = time.time()
nowLocal = time.gmtime(now)
#makeMsg(0,"0","system,kojoney_viz started with pid=" + `pid` + " at localtime " + time.asctime(nowLocal))
a = "kojoney_viz started with pid=" + `pid`

#statusAlert("*** kojoney_viz started ***",a)

# Create a connection to Twitter
#try:
#    TweetClient = twitter.Api(username="honeytweeter",password="fuckfacebook")                
#except Exception,e:
#    syslog.syslog("kojoney_tail.py exception connecting to Twitter : main() : " + `e`)

print "Kill any existing kojoney_tweet.py process(es)..."
os.system('killall kojoney_tweet.py')
time.sleep(5)

print "Kill any existing tcpdump process(es)..."
os.system('killall tcpdump')
time.sleep(3)
print "Erase old pcap file......"
os.system('rm -f /home/var/log/dronetracer.pcap')
print "Start tcpdump to capture C&C traffic at packet level..."
os.system('/usr/sbin/tcpdump -i eth1 -n -s 1500 -U host 172.31.0.67 -w /home/var/log/dronetracer.pcap &')
    
# Set the Kojoney Channel input filename to scan
filename = '/home/var/log/kojoney_tail.log'
file = open(filename,'r')

# Set the DNS input filename to scan
filenamedns = '/var/log/debug'
filedns     = open(filenamedns,'r')

# Set the sebek input filename to scan
filenamesebek = '/home/var/log/kojoney_sebek.csv'
filesebek     = open(filenamesebek,'r')

# Create the fingerprint file
print "Create fresh fingerprint file"
fpOut = open(r'/home/var/log/kojoney_fprint.csv','w')
fpOut.close()

# Run up kojoney_tweet.py
print "Run up kojoney_tweet.py process to Tweet the visualisation file..."
os.system('/home/crouchr/kojoney_tweet.py &')

# Create the fingerprint file
print "sleep 5 seconds to allow kojoney_tweet.py to settle..."
time.sleep(5)

print "Add header to fingerprint file"
now = time.time()
#nowLocal = time.gmtime(now)  
nowLocal = time.localtime(now)  
fpOut = open(r'/home/var/log/kojoney_fprint.csv','a')
print >> fpOut,"DroneTracer : Malware Network Activity Analysis System,(c)2010 Richard Crouch,MD5:" + MalwareMD5 + " analysis started @ " + time.asctime(nowLocal)            
fpOut.close()

print "************************************"
print " Now run malware in the BotTank... *"
print "************************************"
print " "

# Run up kojoney_tweet.py
#print "Run up kojoney_tweet.py procss to Tweet the visualisation file..."
#a = os.system('/home/crouchr/kojoney_tweet.py &')
#print a

# ------------
# tail -f mode
# ------------

# Find the size of the Channel file and move to the end
st_results = os.stat(filename)
st_size = st_results[6]
file.seek(st_size)
print "system     : Seek to end of Kojoney Channel feed"

# Find the size of the DNSMASQ file and move to the end
st_results_dns = os.stat(filenamedns)
st_size_dns = st_results_dns[6]
filedns.seek(st_size_dns)
print "system     : Seek to end of Malware host system dnsmasq DNS feed"

# Find the size of the DNSMASQ file and move to the end
st_results_sebek = os.stat(filenamesebek)
st_size_sebek = st_results_sebek[6]
filesebek.seek(st_size_sebek)
print "system     : Seek to end of Sebek feed"

while True:

    # Kojoney Channel       
    where = file.tell()
    line  = file.readline()

    # DNS - from DNSmasq used solely by Malware
    wheredns = filedns.tell()
    linedns  = filedns.readline()

    # Sebek Channel
    wheresebek = filesebek.tell()
    linesebek  = filesebek.readline()
    
    if not line:		# no data in Kojoney Channel
        #print "nothing in Kojoney Channel logfile to process"
        file.seek(where)
    else:			# new data has been added to log file
        #print "*** NEW EVENT in Kojoney Channel to process !"
        processChannelViz(line)
    
    if not linedns:             # no data in dnsmasq log
        #print "nothing in dnsmasq log file to process" 
        filedns.seek(wheredns)
    else:                       # new data has been added to log file
        #print "*** NEW EVENT in Malware DNS dnsmasq log file to process !"
        processdns(linedns)
    
    if not linesebek:             # no data in dnsmasq log
        #print "nothing in Sebek Channel" 
        filesebek.seek(wheresebek)
    else:                       # new data has been added to log file
        #print "*** NEW EVENT in Sebek Channel to process !"
        processSebek(linesebek)
    
  
    #print "sleeping..."
    # this can be a float for sub-second sleep    
    time.sleep(0.1)	# 10th of a second
    
  
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
            
                                                                        