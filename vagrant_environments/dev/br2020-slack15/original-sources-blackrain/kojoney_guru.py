#!/usr/bin/python

# Look for IP addresses and URLs in tweet_queue.log and add to kojoney_analyst.txt file
# Download but do not process any URLs spotted

# Ignore our own GURU messages

# Example of tweet_queue.log :-
#submitted=Wed Nov  9 05:35:07 2011 cmd=GEO_IP tweet=HONEYTRAP,1433/tcp : 160 bytes from 222.133.189.12:5431.
#submitted=Wed Nov  9 05:35:07 2011 cmd=BASIC tweet=GURU,CN,ip=222.133.189.12 NoDNS CHINA169-BACKBONE AS4837-APNIC 222.132.0.0/14,city=Jinan
#submitted=Wed Nov  9 05:35:10 2011 cmd=BASIC tweet=GURU,CN,ip=222.133.189.12 NoDNS CHINA169-BACKBONE AS4837-APNIC 222.132.0.0/14,city=Jinan
#submitted=Wed Nov  9 05:37:14 2011 cmd=GEO_IP tweet=WEB_SCN,Scan from 66.249.71.168 req=/pmpQDRFM.passwd
#submitted=Wed Nov  9 05:37:17 2011 cmd=BASIC tweet=GURU,US,ip=66.249.71.168 crawl-66-249-71-168.googlebot.com GOOGLE AS15169-ARIN 66.249.71.0/24,city=Mountain View
#submitted=Wed Nov  9 05:38:00 2011 cmd=BASIC tweet=ANALYST,--,TRACEROUTE : HPOT->AS???->AS???->DTAG->CHINA169-BACKBONE->CN:222.133.189.12
#submitted=Wed Nov  9 05:39:46 2011 cmd=GEO_IP tweet=WEB_SCN,Scan from 66.249.71.168 req=/pmpQDRFM.koi8-r
#submitted=Wed Nov  9 05:39:49 2011 cmd=BASIC tweet=GURU,US,ip=66.249.71.168 crawl-66-249-71-168.googlebot.com GOOGLE AS15169-ARIN 66.249.71.0/24,city=Mountain View
#submitted=Wed Nov  9 05:41:34 2011 cmd=BASIC tweet=ANALYST,--,NMAP 222.133.189.12 open={21 80 81 1026 1433 3306} os=Windows ipId=Busy server or unknown class tcpSeq=Difficulty=259 hops=22
#submitted=Wed Nov  9 05:42:20 2011 cmd=GEO_IP tweet=WEB_SCN,Scan from 66.249.71.168 req=/pmpQDRFM.config
#submitted=Wed Nov  9 05:42:23 2011 cmd=BASIC tweet=GURU,US,ip=66.249.71.168 crawl-66-249-71-168.googlebot.com GOOGLE AS15169-ARIN 66.249.71.0/24,city=Mountain View
#submitted=Wed Nov  9 05:44:57 2011 cmd=GEO_IP tweet=WEB_SCN,Scan from 66.249.71.168 req=/junk988.aspx%5C
#submitted=Wed Nov  9 05:44:59 2011 cmd=BASIC tweet=GURU,US,ip=66.249.71.168 crawl-66-249-71-168.googlebot.com GOOGLE AS15169-ARIN 66.249.71.0/24,city=Mountain View
#submitted=Wed Nov  9 05:45:20 2011 cmd=GEO_IP tweet=PASSER,TS 222.133.189.12 TCP_21 ftp://p/Serv-U ftpd/ v/6.4/ o/Windows/
#submitted=Wed Nov  9 05:45:23 2011 cmd=GEO_IP tweet=PASSER,TS 222.133.189.12 TCP_3306 mysql://p/MySQL/ i/unauthorized/
#submitted=Wed Nov  9 05:45:33 2011 cmd=GEO_IP tweet=PASSER,TS 222.133.189.12 TCP_81 http://p/Microsoft IIS httpd/ v/6.0/ o/Windows/
#submitted=Wed Nov  9 05:45:38 2011 cmd=GEO_IP tweet=PASSER,TS 222.133.189.12 TCP_80 http://p/Microsoft IIS httpd/ v/6.0/ o/Windows/
#submitted=Wed Nov  9 05:45:47 2011 cmd=GEO_IP tweet=PASSER,TS 222.133.189.12 TCP_1433 ms-sql-s://p/Microsoft SQL Server 2005/ v/9.00.1399; RTM/ o/Windows/
#submitted=Mon Dec 31 07:17:18 2012 cmd=GEO_IP tweet=WEB_WRITE,Previously unseen PHP malware file facb41b5a686f01dda9559b792dddc38 written to disk
#submitted=Mon Dec 31 07:17:27 2012 cmd=GEO_IP tweet=WEB_WRITE,Previously unseen PHP malware file 32c18a69880ef9ccc3720782cb492d43 written to disk
#submitted=Mon Dec 31 07:17:35 2012 cmd=GEO_IP tweet=WEB_WRITE,Previously unseen PHP malware file 73a53628bafa016afcdb845d1eb2bbb3 written to disk
#submitted=Wed Jan  2 04:40:28 2013 cmd=GEO_IP tweet=WEB_WRITE,Previously unseen PHP malware file a05dfd7cca7771a7565a154d65f05ea2 written to disk
#submitted=Wed Jan  2 04:40:32 2013 cmd=GEO_IP tweet=WEB_WRITE,Previously unseen PHP malware file 1d1b6b908d91ad73f90ea72c4ebe6609 written to disk
#submitted=Wed Jan  2 07:37:31 2013 cmd=GEO_IP tweet=WEB_WRITE,Previously unseen PHP malware file cee64d03132cb654a12612f59bb7e432 written to disk
#submitted=Wed Jan  2 07:37:34 2013 cmd=GEO_IP tweet=WEB_WRITE,Previously unseen PHP malware file 5d00563c08abf308209bb467fdf4911b written to disk

import time, os , syslog , re 
import kojoney_funcs
import ipintellib
import twitter_funcs

#ROUTER = "172.31.0.9"
#HPOT   = "172.31.0.67"
#HONEYD = "172.31.0.1"
#IBG    = "172.31.0.47"	# IP address sending netflow 

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

# Find URL from trojaned wget running on honeypot
# Sep 27 05:57:59 mars wget: Honeypot wget requests URL http://www.openbsd.org/index.html 
# return IP address from URL or None
def processURLfoundWget(line,test=False):

    try :
        line=line.strip("\n")
        print "processURLfoundWget() : line read : " + line
        if line.find("GURU,") != -1 :
            return # Do not process GURU records
                
        if line.find("http://bit.ly") != -1:
            return # probably a Snort IDS xreference
                             
        protocol = None
        if line.find("http://") != -1 :
            protocol = "http://" 
        if line.find("https://") != -1 :
            protocol = "https://" 
        if line.find("tftp://") != -1 :
            protocol = "tftp://" 
        if line.find("ftp://") != -1 :
            protocol = "ftp://" 
            
        # Common case for Kippo is wget www.dfsdsd.com/fd.jpg...
        if line.find("wget") != -1 and protocol == None :
            protocol = "http://" 
            line = "http://" + line.split("wget ")[1]
            #print line
            
        if protocol == None:
            return    
            
        #print "processURLfoundWget() : candidate line read : " + line
        #print "protocol is " + protocol            
        
        url = line[line.find(protocol):]
        
        # Experimental - glastopf seems to add ? or ??
        url=url.rstrip("?")
        url=url.rstrip("?")
        
        print "url is " + url.__str__()
        #t = t[:t.find(" ")]
        # Write the URL to a file to be picked up by kojoney_analyst for download etc
        a = url.split("->")[0]
        # remove any data after the URL like "shellcode=plain" etc.
        a = a.split(" ")
        a = a[0]

        msg = "kojoney_guru.py : found url " + a
        print msg
        
        # **********************************************************
        # Add URL Task to Job Queue for processing by kojoney_anubis
        # **********************************************************
        addUrlToFile(a,test)
                     
        fields = url.split('/')
        #print fields
        domain = fields[2]     # e.g. openbsd.org
        #print "url is " + url

        #surl = url.replace("http://","")
        #surl = surl.split('/')
        #surl = surl[0]

        #print "stripped url is " + surl
        dnsInfo = ipintellib.ip2name(domain)
        ip = dnsInfo['name']
        
        if ip == "127.0.0.1" or ip == "0.0.0.0" :
            return None
                                                                                                                                         
        return ip
    except Exception,e:
        syslog.syslog("kojoney_guru.py : processURLfoundTweet() exception caught = " + `e` + " line=" + line)

# Use wget to download the single malware file
def retrieveSingleURL(url,ip):

    try :
        print "retrieveURL() : url to be downloaded from " + ip + " is " + url
     
        # generate destination filename
        dFilename = url + "--" + ip + "--" + `time.time()`
        #print "retrieveURL() : destination filename : " + dFilename
        
        # not working : bug
        #cmd = "wget -t 3 --directory-prefix=/home/var/haxxor_webs/honeytweeter-downloads --no-check-certificate" + " -O " + dFilename + " " + url 
        cmd = "wget --directory-prefix=/home/var/haxxor_webs/honeytweeter-downloads --no-check-certificate" + " " + url 
        print "retrieveURL() : cmd to be exectuted : " + cmd
        
        result = os.system(cmd)		# returns int
        print "wget result is " + `result`         
        syslog.syslog("kojoney_guru.py retrieveURL() : result=" + `result` + " for " + cmd)

        # Downloading a file changes defcon status
        kojoney_funcs.writeDefconEvent("botwall","haxxor downloaded malware from " + ip + " file=" + url) 
            
    except Exception,e:
        syslog.syslog("kojoney_guru.py : retrieveURL() exception caught = " + `e` + " url=" + url)

# Write tweet to file where it will get picked up by kojoney_tweet and sent
# make this a global function so it can be used elsewhere e.g. by kojoney_analyst
def addTweetToQueue(tweet):
    #print "-----------------"
    print "*** tweet:" + tweet
    
    fpOut = open(r'/home/var/log/kojoney_guru.txt','a')
    print >> fpOut,tweet 
    fpOut.close()

# Write url to a file where it will be picked up by kojoney_anubis
# Add a URL task to Analyst Job Queue
def addUrlToFile(url,test=False):
    now = time.time()
    nowLocal = time.gmtime(now)
    msg = time.asctime(nowLocal) + "," + "URL" + "," + url
    #print "addUrlToFile() : " + msg    
    
    if test == False :
        fpOut = open(r'/home/var/log/kojoney_analyst.txt','a')
    else:
        fpOut = open(r'/home/var/log/kojoney_analyst_testoutput.txt','a')
    print >> fpOut,msg
    fpOut.close()

# Write ANUBIS report URLs to a file where it will be picked up by kojoney_anubis
# Add a ANUBIS task to Analyst Job Queue
def addAnubisURLtoFile(line,test=False):
    try:
        now = time.time()
        nowLocal = time.gmtime(now)
    
        # extract Anubis report URL from tweet
        reportURL = line.split('Analysis :')[1]
        reportURL = reportURL.strip()
  
        msg = time.asctime(nowLocal) + "," + "ANUBIS" + "," + reportURL
        
        if test == False :
            fpOut = open(r'/home/var/log/kojoney_analyst.txt','a')
        else:
            fpOut = open(r'/home/var/log/kojoney_analyst_testoutput.txt','a')
        
        print >> fpOut,msg
        fpOut.close()
    
    except Exception,e:
        syslog.syslog("kojoney_guru.py : addAnubisURLtoFile() : " + e.__str__())            

# Write Glastopf PHP file downloads to a file where it will be picked up by kojoney_anubis
# Add a PHPFILE task to Analyst Job Queue
def addPHPtoFile(line,test=False):
    try:
        now = time.time()
        nowLocal = time.gmtime(now)
    
        # extract PHP MD5 filename from tweet
        fields = line.split("tweet=")[1]
        fields = fields.split(" ")
        phpfilename = fields[5]
  
        msg = time.asctime(nowLocal) + "," + "PHPFILE" + "," + phpfilename
        if test == False:
            fpOut = open(r'/home/var/log/kojoney_analyst.txt','a')
        else:
            fpOut = open(r'/home/var/log/kojoney_analyst_testoutput.txt','a')
        
        print >> fpOut,msg
        print "kojoney_guru.py : addPHPtoFile() : Added following to kojoney_analyst.txt : " + msg.__str__()
        fpOut.close()
    
    except Exception,e:
        syslog.syslog("kojoney_guru.py : addPHPtoFile() : " + e.__str__())            

# Write IP address to a file where it will be picked up by kojoney_analyst
# kojoney_analyst.py then performs traceroute and nmap to the IP
# Add a RECON task to Analyst Job Queue
def addIPtoFile(ip,test=False):

    try:
        if ip == "127.0.0.1":
            return
        
        # Add white list here
        # Slackware patching
        # Twitter API
        # BT Connect SMTP
            
        now = time.time()
        nowLocal = time.gmtime(now)
    
        msg = time.asctime(nowLocal) + "," + "RECON" + "," + ip
        if test == False :
            fpOut = open(r'/home/var/log/kojoney_analyst.txt','a')
        else:
            fpOut = open(r'/home/var/log/kojoney_analyst_testoutput.txt','a')
        print >> fpOut,msg
        fpOut.close()
    
    except Exception,e:
        syslog.syslog("kojoney_guru.py : addIPtoFile() : " + e.__str__())            

# Add an LMD task to Analyst Job Queue
def addLMDtoFile(line,test=False):
    try:
        fields = line.split("tweet=")[1]
        fields = fields.split(" ")
        #print fields
        filepath = fields[1].split("file=")[1]
        
        now = time.time()
        nowLocal = time.gmtime(now)
        msg = time.asctime(nowLocal) + "," + "LMD" + "," + filepath
        
        if test == False :
            fpOut = open(r'/home/var/log/kojoney_analyst.txt','a')
        else:
            fpOut = open(r'/home/var/log/kojoney_analyst_testoutput.txt','a')
        print >> fpOut,msg
        fpOut.close()
    
    except Exception,e:
        syslog.syslog("kojoney_guru.py : addLMDtoFile() : " + e.__str__())            
                                   
# -------------------------------------------------------
        
# Start of code        
syslog.openlog("kojoney_guru",syslog.LOG_PID,syslog.LOG_LOCAL2)         # Set syslog program name         
       
# Make pidfile so we can be monitored by monit        
pid =  makePidFile("kojoney_guru")
if pid == None:
    syslog.syslog("Failed to create pidfile for pid " + `pid`)
    sys.exit(0)
else:
    syslog.syslog("kojoney_guru.py started with pid " + `pid`)
                
# Send an email to say kojoney_tail has started
now = time.time()
nowLocal = time.gmtime(now)
#makeMsg(0,"0","system,kojoney_viz started with pid=" + `pid` + " at localtime " + time.asctime(nowLocal))
a = "kojoney_guru started with pid=" + `pid`

#filenameWget = '/home/var/log/tweets.attempts.log.txt' 		# real file
filenameWget = '/home/var/log/tweet_queue.log'	 			# real file
#filenameWget = '/home/crouchr/kojoney_guru_php_test.txt'		# test PHP analysis

#filenameWget = '/home/var/log/tweets.attempts.log.test'		# testfile

fileWget     = open(filenameWget,'r')
            
# ------------
# tail -f mode
# ------------
test = False
tail = True

# Find the size of the Tweets file and move to the end
print "Test Mode : " + test.__str__()
print "Tail Mode : " + tail.__str__()
         
if tail == True :
    st_resultsWget = os.stat(filenameWget)
    st_sizeWget    = st_resultsWget[6]
    fileWget.seek(st_sizeWget)
    print "system     : Seek to end of Tweet queue : " + filenameWget
else:
    print "system     : Test Mode -> Seek to START of Tweet queue : " + filenameWget
    
ipList = {}                          # list of IPs we have provided network guru information for
     
while True:
        
    whereWget = fileWget.tell()
    lineWget  = fileWget.readline().rstrip()
        
    if not lineWget:		# no data to process
        #print "kojoney_guru.py : nothing in Tweets logfile to process"
        fileWget.seek(whereWget)
    elif lineWget.find("AMUN_AA") != -1 :
        addAnubisURLtoFile(lineWget,test)
        print "\n*** NEW EVENT (AMUN_AA) in Tweet queue to pass onto ANALYST for analysis..."
        print lineWget
    elif lineWget.find("WEB_WRITE,Previously unseen PHP malware file") != -1 :
        print "\n*** NEW EVENT (PHP file downloaded) in Tweet queue to pass onto ANALYST for analysis..."
        print lineWget
        addPHPtoFile(lineWget,test)
    elif lineWget.find("LMD,") != -1 :
        print "\n*** NEW EVENT (Malware File detected by LMD) in Tweet queue to pass onto ANALYST for analysis..."
        print lineWget
        addLMDtoFile(lineWget,test)
    elif lineWget.find("GURU") == -1 and lineWget.find("ANALYST") == -1 and lineWget.find("PASSER") == -1  :	# don't process for these agents
        print "\n*** NEW EVENT in Tweet queue to provide GURU info for..."
        print lineWget
        gid = 0					# guru message Id
        lineWget  = lineWget.strip('"')    
        
        print lineWget

        if lineWget.find(":::") != -1 :
            print "kojoney_guru.py() : Do not provide GURU info for untweeted messages"
            continue
        
        if lineWget.find("tweet=") != -1 :
            tweet = lineWget.split("tweet=")[1]
            
        # Look for N x a.b.c.d IP address
        pat = r'\d+\.\d+\.\d+\.\d+'             # locate a number of IP addresses
        ips = re.findall(pat,tweet)  
        ip = None
            
        # *****************************************************************************
        # Look for 1 x URL i.e. put into JOB Queue for kojoney_anubis to pick out later
        # *****************************************************************************
        ipUrl = processURLfoundWget(tweet,test)
         
        # Case 1 : Generate Tweets for raw IPs found
        # TODO : Need a safety feature to ensure that IPs in range 192.168.1.0/24 are never added to TweetQueue
        if len(ips) != 0 :
                
            # Case #1 : Generate Tweets for raw IPs found
            for ip in ips:
                if ipList.has_key(ip) == False :	# not seen this IP before
                    # Get DNS name
                    dnsInfo = ipintellib.ip2name(ip)
                    dnsName = dnsInfo['name'].rstrip('.') + " "  
                    asMsg   = ipintellib.prettyAS(ip)         
                    
                    geoIP = ipintellib.geo_ip(ip)
                    countryCode = geoIP['countryCode']
                    city        = geoIP['city']
                
                    if city == "?" :
                        geoInfo = ""
                    else:    
                        geoInfo     = "," + "city=" + city
                             
                    gid         = gid + 1
                    #tweet       = "GURU," + countryCode + "," + "ip="  + ip + " " + dnsName + asMsg + geoInfo 
                    tweet       = "GURU,IP "  + ip + " => " + dnsName + asMsg + geoInfo 
                    
                    if tweet.find("192.168.1.") == -1 :
                        twitter_funcs.addTweetToQueue(tweet,geoip=True)
                        # ****************************************************************    
                        # Add the IP to the JOB Queue for kojoney_anubis to pick out later
                        # ****************************************************************    
                        addIPtoFile(ip,test)
                
                    # Add the IP to the cache so we do not provide GURU information for it again
                    ipList[ip] = ip
                
        # Case 2 : Generate Tweets for URLs found
        if ipUrl != None and ipUrl != "NoDNS" :
            print "kojoney_guru.py() : URL IP address = " + ipUrl
            # Get DNS name
            dnsInfo = ipintellib.ip2name(ipUrl)
            dnsName = dnsInfo['name'].rstrip('.') + " "  
            asMsg   = ipintellib.prettyAS(ipUrl)         
        
            geoIP = ipintellib.geo_ip(ipUrl)
            countryCode = geoIP['countryCode']
            city        = geoIP['city']
            
            if city == "?" :
                geoInfo = ""
            else:    
                geoInfo     = "," + "city=" + city
                
            geoInfo     = "," + "city=" + city + " cc=" + countryCode
                
            gid         = gid + 1
            #tweet       = "GURU," + countryCode + "," + "url->"  + ipUrl + " " + dnsName + asMsg + geoInfo 
            tweet       = "GURU,URL "  + ipUrl + " => " + dnsName + asMsg + geoInfo 
            twitter_funcs.addTweetToQueue(tweet,geoip=True)
                
    time.sleep(0.5)	# use 0.5 seconds 
                                                                    