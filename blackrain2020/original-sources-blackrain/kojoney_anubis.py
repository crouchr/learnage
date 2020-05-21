#!/usr/bin/python

import time, os , syslog , re , sys , time
import kojoney_funcs
import ipintellib
import twitter_funcs
import traceroute_matrix
import kojoney_nmap
import kojoney_cymru_hash
import kojoney_hiddenip
import analyse_php_scripts
import kojoney_anubis_idmef
import virustotal
import kojoney_alert_client	# my wrapper for sending email via Googlemail

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
    
# 
# Compute MD5 on a fullpathname
# Make this a comon function
#
def calcMD5(fullFilename):
    try:
        cmd = "/usr/bin/md5sum " + fullFilename.__str__()
        pipe = os.popen(cmd,'r')
        raw = pipe.read().rstrip("\n")
        #print raw
        result = raw.split(" ")[0]
        
        if "No such file" in raw :
            return None
        else:
            return result
            
    except Exception,e:
        msg = "kojoney_anubis.py : calcMD5() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return None
    
# do not perform active reconnaisance into certain countries
def isSafeToScan(ip) :
    #UNSAFE_COUNTRIES = ['?','GB','US','DE']			# if testing using ShieldsUp (US)
    #UNSAFE_COUNTRIES = ['GB']	# Normal
    SAFE_COUNTRIES = ['CN','RU','TW','UA','BR','NL','PL','KZ','JP','FR','VN','JP','TR','BG','AR','MX','TH','IN','HK','KR','NG','JO','IR','IQ','PK','KE','ID','CL','HN','AE','LV','EG','RO','MA','VE','PH']	
    geoIP = {}
    
    try :
        print "*** kojoney_anubis.py : calling hiddenIP() ***"
        # Do not scan Google / Local LAN etc
        if kojoney_hiddenip.hiddenIP(ip) == True :
            msg = "kojoney_anubis.py : isSafeToScan() : " + ip + " is **not** OK to scan according to hiddenIP()"
            print msg
            #syslog.syslog(msg)
            return False
        else:
            msg = "kojoney_anubis.py : isSafeToScan() : " + ip + " is OK to scan according to hiddenIP()"
            print msg
            #syslog.syslog(msg)
        
        # Check the country of the attacker
        geoIP = ipintellib.geo_ip(ip)
        cc = geoIP['countryCode']
        #print cc
        if cc not in SAFE_COUNTRIES:
            msg = ip + " is in " + cc.__str__() + " jurisdiction and so considered UNSAFE to scan"
            #syslog.syslog(msg)
            print msg
            return False
        else:
            msg = ip + " is in " + cc.__str__() + " jurisdiction and so considered safe to scan"
            #syslog.syslog(msg)
            print msg
            return True    
            
    except Exception,e:
        msg = "kojoney_anubis.py : isSafeToScan() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return False

    
# Run the UNIX FILE utility over the malware to determine file type
# note : malwareFilename is generally the full file and pathname
def analyseMalwareFile(malwareFilename,test):
    
    try :
        print "kojoney_anubis.py : analyseMalwareFile() : malwareFilename=" + malwareFilename.__str__()
        
        if "/" in malwareFilename :
            fullFilename = malwareFilename
        else:    
            fullFilename = "/usr/local/src/amun/malware/md5sum/" + malwareFilename.__str__()
        
        a = fullFilename.split("/")
        filename = a[-1]		# -1 = last component
        
        print "analyseMalwareFile() : full path = " + fullFilename.__str__()
        print "analyseMalwareFile() : filename  = " + filename.__str__()
        
        tweet = "ANALYST,FILE "		# YES SO DONT : if I make this ANUBIS does tweet engine get into a loop ?

        cmd = "/usr/local/sbin/file " + fullFilename.__str__()
        print cmd
        pipe = os.popen(cmd,'r')
        
        raw = pipe.read().rstrip("\n")
        print raw      
        if "cannot open" in raw :
            print "kojoney_anubis.py : analyseMalwareFile() : can't open " + malwareFilename.__str__()
            return None
        
        # Extract just the filename, not the full pathname from the result
        a = raw.split("/")
        print "analyseMalwareFile() : a=" + a.__str__()
        #print len(a)
        result = a[-1]	# -1 = the last component i.e. the result from the FILE utility
        print "kojoney_anubis.py : analyseMalwareFile() FILE utility result=" +  result.__str__()
        
        # Shorten Tweets
        result = result.replace("last modified:","mod.")
        result = result.replace("compressed data","compressed")
        
        if raw != None:
            tweet = tweet + result
            #kojoney_alert_client.sendAlert("Malware File Utility Analysis",tweet,True,False)
        else:
            tweet = None
                
        return tweet          
             
    except Exception,e:
        msg = "kojoney_anubis.py : analyseMalwareFile() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return None

# Run ClamAV over the malware to determine file type
# note : malwareFilename is generally the full file and pathname
def analyseMalwareAV(malwareFilename,test):
    try :
        print "kojoney_anubis.py : analyseMalwareAV() : malwareFilename=" + malwareFilename.__str__()
        
        if "/" in malwareFilename :
            fullFilename = malwareFilename	# No path information
            filename = malwareFilename.split("/")[-1]
            md5 = calcMD5(fullFilename)    
        else:    
            fullFilename = "/usr/local/src/amun/malware/md5sum/" + malwareFilename.__str__()
            md5 = malwareFilename.replace(".bin","")
            filename = malwareFilename		# No path information
        
        print "analyseMalwareAV() : fullFilename     = " + fullFilename.__str__()
        print "analyseMalwareAV() : fullFilename MD5 = " + md5.__str__()
        
        # Check #1 : Team Cymru Malware Hash Registry (MHR)
        #md5 = malwareFilename.replace(".bin","")
        #print md5
        cymruPercent = kojoney_cymru_hash.cymruHash(md5)
        print "Check#1 : Team Cymru AV percent = " + cymruPercent.__str__()
      
        # Check #2 : VirusTotal
        vt = virustotal.getVirusTotalFile(md5,"ALL",False)
        if vt['status'] == True:
            print vt['md5']
            print vt['date'] 
            print vt['single']
            print vt['matches']
            print vt['total']  
            print vt['permalink']
            print vt['bitly']
            print "Summary : " + vt['summary']
            tweet = "ANALYST,AV " + filename + " => " + vt['summary']    
        else:                                                                                                                                                                                    
            return None
            
        # Check #3 : Run ClamAV locally
        #cmd = "/usr/local/bin/clamscan " + fullFilename.__str__()
        #pipe = os.popen(cmd,'r')
        #raw = pipe.read().rstrip("\n")
        #print raw
        
        #if raw.find("Can't access file") != -1 :
        #    print "kojoney_anubis.py : analyseMalwareAV() : can't open " + malwareFilename.__str__()
        #    return None
        
        # Extract just the filename, not the full pathname from the result
        #a = raw.split("/")
        ##print a.__str__()
        ##print len(a)
        #result = a[-1]
        #print "Check #2 : ClamAV utility results : " +  result.__str__()
        
        #result = result.split("\n")[0]
        #result = result.replace("FOUND","MW-FOUND")	# make a rare keyword for tweetsOfInterest() to find
        #result = result.replace(filename + ": ","")
        #print "kojoney_anubis.py : analyseMalwareAV() : ClamAV utility results : " +  result.__str__()
        #
        #tweet = "ANALYST" + "," + "--" + ",AV->" + filename + ": ClamAV=" + result
        #if raw != None:
        #    if cymruPercent != None :
        #        tweet = tweet +  ", TeamCymruMHR=" + cymruPercent.__str__() + "%"
        #    #else:
        #    #    tweet = tweet + result
        #else:
        #    tweet = None
        
        return tweet          
             
    except Exception,e:
        msg = "kojoney_anubis.py : analyseMalwareAV() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return None

# Download Anubis report
# Call to function to analyse it
# Tweet if network activity found and the name of the malware if found
def analyseAnubisReport(url,test):
    
    try :
        malwareFilename = None
        tweet = "ANALYST,SANDBOX "	# if I make this ANUBIS does tweet engine get into a loop ?
        
        print "url : " + url.__str__()
        reportUrl = url + "&format=txt"
        
        # make it easier to delete reports downloaded as part of testing
        if test == True :
            reportFilename = "/home/var/haxxor_webs/kojoney_analyst/anubis/" + "test-anubis-" + time.time().__str__() + ".txt"
        else:
            reportFilename = "/home/var/haxxor_webs/kojoney_analyst/anubis/" + "anubis-" + time.time().__str__() + ".txt"
        
        cmd = "wget --timeout 30 -q -t 2 -nc --no-check-certificate" + " '" + reportUrl + "'" + " -O " + reportFilename 
        print "analyseURL() : cmd to be exectuted : " + cmd
        result = os.system(cmd)		# returns int
        #print "wget result is " + result.__str__()         
        #syslog.syslog("kojoney_anubis.py retrieveURL() : wget result=" + result.__str__() + " for " + cmd)
        
        if result != 0 :
            msg = "kojoney_anubis.py : analyseAnubis Report() : wget returned non-zero (failure) result=" + result.__str__()
            syslog.syslog(msg)
            print msg
            return None,None
        
        # If Anubis is busy with many analysis jobs in it's queue, then we can't get the report now
        queued = anubisJobQueued(reportFilename)
        if queued == True :
            tweet = tweet + "Malware analysis queued in Anubis Analysis Queue"    
            return tweet,None
        
        filename = getMD5fromFile(reportFilename)
        if filename != None:
            tweet = tweet + filename.__str__()
            #malwareFilename = "/usr/local/src/amun/malware/md5sum/" + filename.__str__() + ".bin"
            malwareFilename = filename.__str__() + ".bin"
            
        fprint = getFingerprint(reportFilename)
        if fprint != None:
            tweet = tweet + " : " + fprint.__str__()
        
        print "kojoney_anubis.py : analyseAnubisReport() : tweet=" + tweet.__str__()
        print "kojoney_anubis.py : analyseAnubisReport() : malwareFilename=" + malwareFilename.__str__()
        #print malwareFilename
        #kojoney_alert_client.sendAlert("Anubis Sandbox Analysis",tweet,True,False)
        return tweet,malwareFilename
             
    except Exception,e:
        msg = "kojoney_anubis.py : analyseAnubisReport() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return None,None

# open Anubis file and look for the MD5 signature
def getMD5fromFile(fullpathname):
    try:
        f=open(fullpathname)
        for line in f.readlines():
            if line.find("MD5:") != -1 :
                line=line.split(":")[1]
                line=line.strip(" ")
                line=line.strip()
                return line             
        return None
    except Exception,e:
        msg = "kojoney_anubis.py : getMD5fromFile() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return None

# open Anubis malare analysis report and look for the keywords
def getFingerprint(fullpathname):
    try:
        # only report fingerprint aspects once
        netDetected = False
        dnsDetected = False
        tcpDetected = False
        ircDetected = False
        fwDetected  = False
        
        fprint = ""
        f=open(fullpathname)
        for line in f.readlines():
            if line.find("No threats could be detected") != -1 :
                fprint = fprint + " NO-THREAT"
            if line.find("Execution did not terminate") != -1 :
                fprint = fprint + " CRASHED"
            if line.find("Packed Binary:") != -1 :
                fprint = fprint + " PACKED"
            if line.find("Network Activities") != -1 and netDetected == False :	# only report once
                fprint = fprint + " NET"
                netDetected = True
            if line.find("DNS Queries") != -1 and dnsDetected == False :	# only report once
                fprint = fprint + " DNS"
                dnsDetected = True
            if line.find("TCP Traffic") != -1 and tcpDetected == False :	# only report once
                fprint = fprint + " TCP"
                tcpDetected = True
            if (line.find("JOIN") != -1 or line.find("PRIVMSG") != -1) and ircDetected == False :	# only report once
                fprint = fprint + " IRC"
                ircDetected = True
            if line.find("Performs Registry Activities") != -1 :
                fprint = fprint + " REG"
            if line.find("Write to foreign memory") != -1 :
                fprint = fprint + " F_MEM"
            if line.find("Modify system files") != -1 :
                fprint = fprint + " MOD_FILES"
            if line.find("Creates files") != -1 :
                fprint = fprint + " ADD_FILES"
            if line.find("destructs files which") != -1 :
                fprint = fprint + " DEL_FILES"
            if line.find("Spawns Processes") != -1 :
                fprint = fprint + " SPAWN"
            if line.find("Autostart capabilities") != -1 :
                fprint = fprint + " AUTOSTART"
            #if line.find("Sig-Id:") != -1 :
            #    fprint = fprint + " AV"
            if line.find("Windows Firewall") != -1 and fwDetected == False:
                fprint = fprint + " FW"
                fwDetected = True            
        fprint = fprint.strip(" ")	# strip leading / trailing spaces
        return fprint
                     
    except Exception,e:
        msg = "kojoney_anubis.py : getFingerprint() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return None
#
#
def anubisJobQueued(fullpathname) :
    try:
        f=open(fullpathname)
        for line in f.readlines():
            if line.find("jobs in queue") != -1 :
                return True
                
        return False             
        
    except Exception,e:
        msg = "kojoney_anubis.py : anubisJobQueued() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return True

#
# Write ip,port to file for use in Afterglow
# portsList is the full list - i.e. may have a large number of ports
def vizNmap(ip,portsList) :
    vizFile = "/home/var/secviz/nmap.csv"
    
    try:
        geoIP = ipintellib.geo_ip(ip)
        cc = geoIP['countryCode']
        print cc
    
        # Too many open ports - maybe a honeypot ?
        # bug : move it out of here since honeypot detection shoudl not be linked to visualisation
        if len(portsList) > 20 :
            msg = "vizNmap() : " + ip + " has too many open ports associated : suspected honeypot"
            print msg
            #syslog.syslog(msg)
            fp = open(vizFile,'a')
            msg = ip + ":" + cc + "," + "SUSPECTED HONEYPOT"
            print >> fp,msg 
            fp.close()
            return
        
        fp = open(vizFile,'a')
        for port in portsList :
            msg = ip + ":" + cc + "," + port.__str__()
            print "vizNmap() : " + msg
            print >> fp,msg 
        fp.close()
        
    except Exception,e:
        msg = "kojoney_anubis.py : vizNmap() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return

# Taken from kojoney_analyst.py - will replace it
# Use wget to download the single malware file
# nc = noclobber = do not download if already downloaded
# return a list of Tweets
def analyseURL(url,test):

    try :
        tweetList = []
        result = -1
        
        # remove any trailing arguments
        url = url.split(" ")
        url = url[0]
        print "url : " + url.__str__()
        
        urlCanon = url.lower()
        print urlCanon
                                
        if urlCanon.find("tftp:") != -1 :       # wget can't do tftp - need a new function
            return None
        if urlCanon.find("iso") != -1 :
            return None
        if urlCanon.find("microsoft") != -1 :
            return None
                                                                                         
        filename = url.split('/')[-1]	# keep last component after split
        fullFilename = "/home/var/haxxor_webs/kojoney_analyst/" + filename.__str__()                                                                                        
                
        # Step 1 : Download the file
        print "filename     : " + filename.__str__()
        print "fullFilename : " + fullFilename.__str__()

        cmd = "wget --timeout 30 -q -t 2 -nc -P /home/var/haxxor_webs/kojoney_analyst --no-check-certificate" + " " + url.__str__()
        print "kojoney_anubis.py : analyseURL() : cmd to be exectuted : " + cmd
                                                                                                                   
        #if test == True:
        #    print "Test mode so do not download the file"
        #    return None
                                                                                                                                                      
        wgetResult = os.system(cmd)         	# returns int
        
        if wgetResult == 0 :                	# success
            msg = "kojoney_anubis.py : analyseURL() : download OK, wgetResult=" + wgetResult.__str__() + " for " + url.__str__()
            #syslog.syslog(msg)
            print msg
            #tweet = "ANALYST" + "," + "--" + "," + "DL=" + url + ", MD5=" + calcMD5(fullFilename)
            fileMD5 = calcMD5(fullFilename)
            tweet = "ANALYST,DLOAD=" + filename + " => MD5=" + fileMD5
            tweetList.append(tweet)
            kojoney_anubis_idmef.sendFiledownloadIDMEF(url,fullFilename,filename,fileMD5,"succeeded","None")
        else:
            msg = "kojoney_anubis.py : analyseURL() : download failed, abort analysis, wgetResult=" + wgetResult.__str__() + " for " + url.__str__()
            syslog.syslog(msg)
            kojoney_anubis_idmef.sendFiledownloadIDMEF(url,fullFilename,filename,None,"failed","None")
            return None				# no point in further analyis if can't download the file
                   
        # Step 2 : Run file through *NIX "file" utility
        tweet = analyseMalwareFile(fullFilename,test)
        if tweet != None:
            tweetList.append(tweet) 
                
        # Step 3 : Run file through ClamAV
        tweet = analyseMalwareAV(fullFilename,test) 
        if tweet != None:
            tweetList.append(tweet) 
                
        #print "tweetList[] = " + tweetList.__str__()
        return tweetList        
                       
    except Exception,e:
        msg = "kojoney_anubis.py : analyseURL() : exception : " + e.__str__() + " url=" + url.__str__()
        print msg
        syslog.syslog(msg)
        return None


# ----------------------------------------------
# why not make this code also analyse URL jobs ?
# ----------------------------------------------

def main():

    ipTracerouted = {}				# list of IPs we have tracerouted Today
    ipNmapped     = {}				# list of IPs we have nmapped today
    
    # Allows for easier debugging - normally all should be set to True
    DO_PHP_JOB    = True
    DO_RECON_JOB  = True
    DO_ANUBIS_JOB = True
    DO_URL_JOB    = True
    DO_LMD_JOB    = True
    
    ############
    test = True
    test = False
    ############
    
    # Start of code        
    syslog.openlog("kojoney_anubis",syslog.LOG_PID,syslog.LOG_LOCAL2)         # Set syslog program name         
    print "started, test=" + test.__str__()
       
    # Make pidfile so we can be monitored by monit        
    pid =  makePidFile("kojoney_anubis")
    if pid == None:
        syslog.syslog("Failed to create pidfile for pid " + `pid`)
        sys.exit(0)
    else:
        syslog.syslog("kojoney_anubis.py started with pid " + `pid`)
                
    # kojoney_guru populates the kojoney_analyst.txt file with jobs to analyse
    if test == True :
        filename = '/home/var/log/kojoney_analyst_test.txt' 			
    else :
        filename = '/home/var/log/kojoney_analyst.txt' 			
    
    fp = open(filename,'r')
            
    # ------------
    # tail -f mode
    # ------------

    # Find the size of the Job file and move to the end
    st_results = os.stat(filename)
    
    if test == False :	# test mode starts at start of file
        st_size    = st_results[6]
        fp.seek(st_size)
        print "kojoney_anubis.py : Seek to END of Analyst Job file " + filename
    else:
        print "kojoney_anubis.py : Seek to START of Analyst Job file " + filename

    ######
    #sys.exit()
    ######
    
    while True:
        tweet = None               
        RECON_DELAY = 300 	# leave enough for Blackhole to have been removed
                    
        where = fp.tell()
        line  = fp.readline().rstrip()
        
        if not line:		# no data to process
            #print "kojoney_anubis.py : nothing in Analyst Job file to process"
            fp.seek(where)
        else :			
            print " "
            print "***********************************************************"
            print "kojoney_anubis.py : NEW EVENT in Analyst jobfile to analyse"
            print "***********************************************************"
            print line
            
            fields    = line.split(",")
            print "JOB : " + fields.__str__()
            jobType = fields[1]	
            #print "kojoney_anubis.py : jobType = " + jobType
            
            #if jobType   == "URL":
            #    tweet = analyseURL(fields[2],test) 
            
            if jobType == "PHPFILE" and DO_PHP_JOB == True :
                print "\n----------------------------------------------------------------------"
                print "                         PHP Malware Analysis" 
                print "----------------------------------------------------------------------\n"
                msg = "kojoney_anubis.py : Detected that a file has been downloaded by Glastopf via RFI attack, so analyse it..."
                #syslog.syslog(msg)
                
                print "JOB = " + line
                phpfilename = "/usr/local/src/glastopf/files/get/" + fields[2]	# fields[2] = MD5 name
                msg = "PHP file to be analysed : " + phpfilename 
                print msg
                #syslog.syslog(msg)
                
                tweet = analyse_php_scripts.makeTweet(phpfilename)
                if tweet == None :
                    tweet = "ANALYST,BOTJUICER=" + fields[2] + " => Indeterminate analysis"
                else:
                    kojoney_alert_client.sendAlert("Botjuicer Analysis",tweet,True,False)
                    tweet = "ANALYST,BOTJUICER=" + tweet
                
                # Send IDMEF to Prelude SIEM
                kojoney_anubis_idmef.botjuicePHPIDMEF(phpfilename,tweet)
                
                if tweet != None:
                    if test != True:
                        twitter_funcs.addTweetToQueue(tweet)
                    else:
                        print "*** Tweet (TestMode) : " + tweet
                
            elif jobType == "ANUBIS" and DO_ANUBIS_JOB == True :
                print "\n----------------------------------------------------------------------"
                print "                   Anubis Win32 Malware Analysis" 
                print "----------------------------------------------------------------------\n"
                msg = "kojoney_anubis.py : Detected that an Anubis Malware Report may be ready, so wait for 10 minutes and then download and analyse it..."
                print "JOB = " + line
                #syslog.syslog(msg)
                if test != True:
                    time.sleep(600) 
                    
                # Step 1 : Analyse the Anubis Report
                tweet,malwareFilename = analyseAnubisReport(fields[2],test) 
                
                if tweet != None:
                    if test != True:
                        kojoney_alert_client.sendAlert("Anubis Analysis",tweet,True,False)
                        twitter_funcs.addTweetToQueue(tweet)
                    else:
                        print "*** Tweet 1 : " + tweet
                else:		# There is no filename so go to next JOB
                    print "kojoney_anubis.py : main() : Tweet 1 : could not open file so aborting remaining analysis"
                    continue
                    
                # Step 2 : Run file through *NIX "file" utility
                #tweet = analyseMalwareFile(fields[2],malwareFilename,test) 
                tweet = analyseMalwareFile(malwareFilename,test) 
                
                if tweet != None:
                    if test != True:
                        kojoney_alert_client.sendAlert("File Analysis",tweet,True,False)
                        twitter_funcs.addTweetToQueue(tweet)
                    else:
                        print "*** Tweet 2 : " + tweet
                else:	# There is no filename so go to next JOB
                    print "kojoney_anubis.py : main() : Tweet 2 : could not open file so aborting remaining analysis"
                    continue
                
                # Step 3 : Run file through ClamAV
                if tweet != None:	# i.e. from Step 2
                    tweet = analyseMalwareAV(malwareFilename,test) 
                
                    if tweet != None:
                        if test != True:
                            kojoney_alert_client.sendAlert("AV Analysis",tweet,True,False)
                            twitter_funcs.addTweetToQueue(tweet)
                        else:
                            print "*** Tweet 3 : " + tweet
            
            elif jobType == "LMD" and DO_LMD_JOB == True :
                print "\n----------------------------------------------------------------------"
                print "                   LMD Malware Analysis" 
                print "----------------------------------------------------------------------\n"
                msg = "kojoney_anubis.py : Detected that malware was detected by LMD so analyse it..."
                print "JOB = " + line
                #syslog.syslog(msg)
                        
                # Step 1 : Run file through *NIX "file" utility
                #tweet = analyseMalwareFile(fields[2],malwareFilename,test) 
                filepath = fields[2]
                tweet = analyseMalwareFile(filepath,test) 
                
                if tweet != None:
                    if test != True:
                        # bug : commented out since fires at 05:00 every morning
                        #kojoney_alert_client.sendAlert("LMD File Analysis",tweet,True,False)
                        twitter_funcs.addTweetToQueue(tweet)
                    else:
                        print "*** Tweet 1/2 : " + tweet
                else:	# There is no filename so go to next JOB
                    print "kojoney_anubis.py : main() : Tweet 2 : could not open file so aborting remaining analysis"
                    continue
                
                # Step 2 : Run file through ClamAV
                if tweet != None:	# i.e. from Step 2
                    tweet = analyseMalwareAV(filepath,test) 
                
                    if tweet != None:
                        if test != True:
                            # bug : commented out since fires at 05:00 every morning
                            #kojoney_alert_client.sendAlert("LMD AV Analysis",tweet,True,False)
                            twitter_funcs.addTweetToQueue(tweet)
                        else:
                            print "*** Tweet 2/2 : " + tweet
            
            elif jobType == "URL" and DO_URL_JOB == True :
                print "\n----------------------------------------------------------------------"
                print "                         URL download and Malware Analysis" 
                print "----------------------------------------------------------------------\n"
                print "JOB = " + line
                msg = "kojoney_anubis.py : Detected that a URL has appeared in the tweet_queue.log file, so download and analyse it..."
                print msg
                #syslog.syslog(msg)
                    
                tweetList = analyseURL(fields[2],test) 
                if tweetList != None :
                    for tweet in tweetList:
                        print "*** Tweet *** : " + tweet
                        if test != True :
                            kojoney_alert_client.sendAlert("Snarfed File Analysis",tweet,True,False)
                            twitter_funcs.addTweetToQueue(tweet,geoip=True)
                        
            elif jobType == "RECON" and DO_RECON_JOB == True :
                ip = fields[2]
                
                print "\nkojoney_anubis.py : Tracerouted IPs cache ->"
                print ipTracerouted
                if isSafeToScan(ip) == False :
                    continue				# go to top of loop i.e. next IP
                #else:
                #    continue				# force to not do traceroute until time blackhole is smarter
                        
                if ipTracerouted.has_key(ip) == False :
                #if ip not in ipList :
                    #ipList.append(ip)
                    print "\n----------------------------------------------------------------------"
                    print "                Step 1 : Reconnaissance (traceroute)                    " 
                    print "----------------------------------------------------------------------\n"
                    print "JOB = " + line
                    msg = ip + " has not been actively tracerouted Today"
                    print msg         
                    #syslog.syslog(msg)
                    
                    #syslog.syslog("sleep for " + RECON_DELAY.__str__() + " seconds and then traceroute " + ip)
                    
                    if test != True:
                        print "sleeping for " + RECON_DELAY.__str__() + " seconds..."
                        time.sleep(RECON_DELAY)			# leave the host alone for a bit... 
                    
                    # Step 4 : Traceroute to the attacker
                    asPath = traceroute_matrix.traceroute("HPOT",ip,30) 
                    if asPath != None:
                        tweet = "ANALYST,TRACEROUTE "
                        tweet = tweet + '->'.join(asPath)
                        # obscure my AS !
                        #tweet = tweet.replace("BT-UK-AS","AS???")
                        #tweet = tweet.replace("->BT","->AS???")
                        tweet = tweet.replace("BT-UK-AS","ISP")
                        tweet = tweet.replace("->BT","->ISP")
                        tweet = tweet.replace("->ISP->ISP","->ISP")
                        ipTracerouted[ip] = tweet	# cache the results
                else:
                    #tweet = ipTracerouted[ip]        
                    tweet = None
                
                msg = "Number of unique IPs tracerouted to since process re-start : " + len(ipTracerouted).__str__()
                #syslog.syslog(msg)
                
                # Send info to Prelude SIEM             
                kojoney_anubis_idmef.tracerouteIDMEF(ip,tweet)
     
                if test != True :
                    if tweet != None:
                        twitter_funcs.addTweetToQueue(tweet,geoip=True)
                
                # nmap the attacker
                # =================    
                print "\nkojoney_anubis.py : Nmapped IPs cache ->"
                print ipNmapped
                
                if ipNmapped.has_key(ip) == False :
                #if True == False :	#  uncomment this to disable this function : bypass this until a way of not clogging DSL can be found
                    print "\n----------------------------------------------------------------------"
                    print "                Step 2 : Reconnaissance (nmap)                          " 
                    print "----------------------------------------------------------------------\n"
                    print "kojoney_anubis.py : " + ip + " has not been actively nmapped Today"
                    
                    print "kojoney_anubis.py : sleep for " + RECON_DELAY.__str__() + " seconds and then Nmap " + ip 
                    if test != True:
                        time.sleep(RECON_DELAY)			# leave the host alone for a bit... 
                    
                    openPorts,closedPorts,hops,osService,uptime,ipid,tcpSeq,hostname = kojoney_nmap.nmapScan(ip)
                    
                    # Add an entry to daily viz file for nmap scans
                    vizNmap(ip,openPorts)
                        
                    tweet = "ANALYST,NMAP " + ip + " " 
                    if len(openPorts) > 20 :
                        tweet = tweet + "open={" + len(openPorts).__str__() + " ports}" 
                    else:
                        tweet = tweet + "open={"
                        tweet = tweet + ' '.join(openPorts)
                        tweet = tweet + "}" 
                        
                    if osService != "?" :	
                        tweet = tweet + " os=" + osService
                    
                    if uptime != "?" :	
                        tweet = tweet + " up=" + uptime
                    
                    if ipid != "?" :	
                        tweet = tweet + " ipId=" + ipid
                    
                    if tcpSeq != "?" :	
                        tweet = tweet + " tcpSeq=" + tcpSeq
                    
                    if hops != None:
                        tweet = tweet + " hops=" + hops
                        
                    ipNmapped[ip] = tweet		# cache the results
                else:
                    #tweet = ipNmapped[ip]    
                    tweet = None        
                
                # Send info to Prelude SIEM             
                kojoney_anubis_idmef.nmapIDMEF(ip,tweet)
         
                print "kojoney_anubis.py : nmap tweet = " + tweet.__str__()
                
                if test != True:
                    if tweet != None :
                        twitter_funcs.addTweetToQueue(tweet,geoip=True)
                   
        if test != True:
            time.sleep(10)	# large delay since events in this channel are rare
        
        
if __name__ == '__main__':
    main()           
