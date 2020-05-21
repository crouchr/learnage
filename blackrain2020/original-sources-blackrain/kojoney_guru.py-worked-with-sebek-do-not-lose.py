#!/usr/bin/python

# Look for messages in honeypot.syslog from trojaned wget command
# & download the file for later analysis

import time, os , syslog , re 
import kojoney_funcs
import ipintellib

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

# make this a library function - it appears in multiple places
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
        syslog.syslog("kojoney_guru.py : statusAlert() : " + `e`)

#URL_FOUND,http://web.clicknet.ro/mirel19/sur.tgz->IP=86.35.15.210,WHOIS=AS9050 (RTD),GeoIP=RO Bucharest 26.10E:lat=44.433300018310547 long=<type 'long'>
#URL_FOUND,http://mau.visual18k.ro/exploit/x.tar->IP=96.9.153.214,WHOIS=AS21788 (NOC),GeoIP=US Scranton -75.65E:lat=41.420101165771484 long=<type 'long'>
#URL_FOUND,http://mau.visual18k.ro/exploit/x.tar->IP=96.9.153.214,WHOIS=AS21788 (NOC),GeoIP=US Scranton -75.65E:lat=41.420101165771484 long=<type 'long'>
# note : some issue with longitude above (to be fixed bug)
#def processURLfoundTweet(line):
#
#    try :
#        line=line.strip("\n")
#        print "processURLfoundTweet() : line read : " + line
#                        
#        if line.find("URL_FOUND") == -1 :
#            return 
#            
#        print "processURLfoundTweet() : candidate line read : " + line
#                    
#        a = line.split(",")[2]          
#        
#        url = a.split("-")[0]
#        print url
#        
#        ip = a.split(">")[1]
#                                                                                                                                                                                           
#        #    fpOut = open(r'/home/var/log/kojoney_tail_tweets.csv','a')
#        #    print >> fpOut,msg 
#        #    fpOut.close()
#        
#        # Download single URL
#        retrieveSingleURL(url,ip)                                                                                                                                 
#    
#    except Exception,e:
#        syslog.syslog("kojoney_guru.py : processURLfoundTweet() exception caught = " + `e` + " line=" + line)

# Find URL from trojaned wget running on honeypot
# Sep 27 05:57:59 mars wget: Honeypot wget requests URL http://www.openbsd.org/index.html 
def processURLfoundWget(line):

    try :
        line=line.strip("\n")
        print "processURLfoundWget() : line read : " + line
                        
        if line.find("Honeypot wget requests URL") == -1 :
            return 
            
        print "processURLfoundWget() : candidate line read : " + line
                    
        fields = line.split()
        print fields
        url = fields[9]
        print "url is " + url

        surl = url.replace("http://","")
        surl = surl.split('/')
        surl = surl[0]

        print "stripped url is " + surl
        dnsInfo = ipintellib.ip2name(surl)
        ip = dnsInfo['name']
        
        #ip = a.split(">")[1]
        #ip = "0.0.0.0"	# bug -> extract the IP from here
                                                                                                                                                                                           
        #    fpOut = open(r'/home/var/log/kojoney_tail_tweets.csv','a')
        #    print >> fpOut,msg 
        #    fpOut.close()
        
        # Download single URL
        retrieveSingleURL(url,ip)                                                                                                                                 
    
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

                                   
# -------------------------------------------------------
        
# Start of code        
syslog.openlog("kojoney_guru")         # Set syslog program name         
       
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

#statusAlert("*** kojoney_tweet started ***",a)

# Method 1
# Set the Tweets log filename to scan, looking for URLs found from Sebek
#filename = '/home/var/log/tweets.log.txt'
#file = open(filename,'r')

# Method 2
# Look for following message in honeypot.syslog
#Sep 27 05:57:59 mars wget: Honeypot wget requests URL http://www.openbsd.org/index.html 
# This is more reliable since it does not suffer from sebek [BS] issue
filenameWget = '/home/var/log/honeypot.syslog'
fileWget = open(filenameWget,'r')

# ------------
# tail -f mode
# ------------

# Find the size of the Tweets file and move to the end
#st_results = os.stat(filename)
#st_size = st_results[6]
#file.seek(st_size)
#print "system     : Seek to end of Tweets log feed"

# Find the size of the honeypot syslog file and move to the end
st_resultsWget = os.stat(filenameWget)
st_sizeWget = st_resultsWget[6]
fileWget.seek(st_sizeWget)
print "system     : Seek to end of Honeypot syslog file"

while True:
    
    # Tweets log file       
    #where = file.tell()
    #line  = file.readline()
    #    
    #if not line:		# no data to process
    #    print "nothing in Tweets logfile to process"
    #    file.seek(where)
    #else :			# new data has been added to log file
    #    print "*** NEW EVENT in Tweet file to process !"
    #    processURLfoundTweet(line)
            
    # Honeypot syslog file       
    whereWget = fileWget.tell()
    lineWget  = fileWget.readline()
        
    if not lineWget:		# no data to process
        print "nothing in Honeypot logfile to process"
        fileWget.seek(whereWget)
    else :			# new data has been added to log file
        print "*** NEW EVENT in Honeypot logfile to process !"
        processURLfoundWget(lineWget)
                    
    #print "sleeping..."
    # this can be a float for sub-second sleep    
    time.sleep(5)	# large delay since do not need to download malware in real-time
                                                                          