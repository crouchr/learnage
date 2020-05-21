#!/usr/bin/python
#
# Look for URL jobs in file and wget them - do not perform any analysis 
# Future : Replace this functionality with kojoney_anubis.py

# input file
# RECON = nmap etc the attacker
#Tue Nov  8 11:39:06 2011,RECON,83.170.193.178
#Tue Nov  8 11:40:34 2011,URL,http://146.185.246.75:80/n3.exe
#Tue Nov  8 11:40:45 2011,RECON,81.91.235.171
#Tue Nov  8 11:40:50 2011,RECON,146.185.246.75
#Tue Nov  8 11:40:54 2011,ANUBIS,http://anubis.iseclab.org/?action=result&task_id=18b689226107c1c54ad4303daccb0d94a
#Tue Nov  8 11:42:29 2011,RECON,66.249.68.138

import time, os , syslog , re , sys , time
import kojoney_funcs
import ipintellib
import twitter_funcs

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


# Use wget to download the single malware file
# nc = noclobber = do not download if already downloaded
def analyseURL(url,test):

    try :
        result = -1
        urlCanon = url.lower()
        print urlCanon
        
        if urlCanon.find("tftp:") != -1 :	# wget can't do tftp - need a new function
            return None
        if urlCanon.find("iso") != -1 :
            return None
        if urlCanon.find("microsoft") != -1 :
            return None
        
        cmd = "wget -q -t 2 -nc -P /home/var/haxxor_webs/kojoney_analyst --no-check-certificate" + " " + url 
        print "analyseURL() : cmd to be exectuted : " + cmd
        
        if test == True:
            print "Test mode so do not download the file"
            return None
        
        result = os.system(cmd)		# returns int
        print "wget result is " + `result`         
        syslog.syslog("kojoney_analyst.py retrieveURL() : result=" + `result` + " for " + cmd)
        
        if result == 0 :		# success
            tweet = "ANALYST" + "," + "--" + "," + "Successfully downloaded file " + url
            return tweet
        return None
    
    except Exception,e:
        syslog.syslog("kojoney_analyse.py : analyseURL() exception caught = " + `e` + " url=" + url)
                                   
# -------------------------------------------------------

def main():
    
    test = False    
    #test = True    
    
    # Start of code        
    syslog.openlog("kojoney_analyst",syslog.LOG_PID,syslog.LOG_LOCAL2)         # Set syslog program name         
    print "started, test=" + test.__str__()
       
    # Make pidfile so we can be monitored by monit        
    pid =  makePidFile("kojoney_analyst")
    if pid == None:
        syslog.syslog("Failed to create pidfile for pid " + `pid`)
        sys.exit(0)
    else:
        syslog.syslog("kojoney_analyst.py started with pid " + `pid`)
                
    # kojoney_guru populates the kojoney_analyst.txt file with URLs for kojoney_analyst to analyse
    filename  = '/home/var/log/kojoney_analyst.txt' 			
    fp        = open(filename,'r')
            
    # ------------
    # tail -f mode
    # ------------

    # Find the size of the Job file and move to the end
    st_results = os.stat(filename)
    
    if test == False :	# test mode starts at start of file
        st_size    = st_results[6]
        fp.seek(st_size)
        print "system     : Seek to end of Analyst Job file"
    else:
        print "system     : Test mode -> Seek to START of Analyst Job file"

    while True:
        tweet = None               
    
        where = fp.tell()
        line  = fp.readline().rstrip()
        
        if not line:		# no data to process
            #print "kojoney_analyst.py : nothing in Analyst Job file to process"
            fp.seek(where)
        else :			
            print "\n*** NEW EVENT in Analyst jobfile to analyse..."
            print line
            
            fields    = line.split(",")
            #print fields
            jobType = fields[1]	
        
            if jobType   == "URL":
                url = fields[2]
                tweet = analyseURL(url,test)
                print "kojoney_analyst.py : jobType=" + jobType.__str__() + " url=" + url.__str__() 
            #elif jobType == "ANUBIS":
            #    tweet = analyseAnubisReport(fields[2],test) 
                
            if tweet != None:
                if test != True:
                    twitter_funcs.addTweetToQueue(tweet)
                else:
                    print "Tweet : " + tweet
                
        if test != True:
            time.sleep(1)	# use 3 seconds : large delay since do not need to download malware in real-time
        else:
            time.sleep(0.001)	# even a miniscule delay means you can CTRL-C the process
                    
if __name__ == '__main__':
    main()           
