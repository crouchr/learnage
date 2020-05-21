#!/usr/bin/python


import time, os , syslog , re 
import kojoney_funcs
import ipintellib
import twitter_funcs
import kojoney_correlate
import shelve


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
    
    
# Filter out the common events - need to make this more sophisticated i.e. use correlation    
# This is only needed for Tweets that do not contain IP addresses
def suppressTweet(tweet):    
    try:
        # if honeyd and tcp and Windows OS then too many to tweet
        #if tweet.find("HONEYD_FLOW") != -1 and tweet.find("tcp") != -1 and tweet.find("os=Windows") != -1 :
        #    syslog.syslog("kojoney_tweet_engine.py : suppressTweet() : " + tweet)
        #    return None

        if tweet.find("RTR_AUTH") != -1 and tweet.find("Carrier dropped") != -1 :
            syslog.syslog("suppressTweet() : " + tweet)
            return None

        # do not tweet the not so interesting Tweets
        if "ANALYST,NMAP" in tweet :
            return None
        if "ANALYST,TRACEROUTE" in tweet :
            return None
            
        if "WEB_SCN," in tweet :
            return None
        if "WEB_PRX," in tweet :
            return None
        if "GURU,IP" in tweet :
            return None
        if "DEFEND," in tweet :
            return None
                    
        return tweet      
             
    except Exception,e:    
        syslog.syslog("suppressTweet() : exception caught = " + `e` + " tweet=" + tweet)
                                   
                                   
# -------------------------------------------------------
        
# Start of code        
syslog.openlog("kojoney_tweet_engine",syslog.LOG_PID,syslog.LOG_LOCAL2)         # Set syslog program name         
       
# Make pidfile so we can be monitored by monit        
pid =  makePidFile("kojoney_tweet_engine")
if pid == None:
    syslog.syslog("Failed to create pidfile for pid " + `pid`)
    sys.exit(0)
else:
    syslog.syslog("kojoney_tweet_engine.py started with pid " + `pid`)
                
# Send an email to say kojoney_tail has started
now = time.time()
nowLocal = time.gmtime(now)
a = "kojoney_tweet_engine started with pid=" + `pid`

filename = '/home/var/log/tweet_queue.log' 			# real file
file     = open(filename,'r')
            
# ------------
# tail -f mode
# ------------

# Find the size of the Tweets queue file and move to the end
st_results = os.stat(filename)
st_size    = st_results[6]
file.seek(st_size)

print "system     : Seek to end of Tweets queue " + filename

try:
    while True:        
        where = file.tell()
        line  = file.readline().rstrip()
        #print "\nline=" + "[" + line + "]"
        l     = len(line)
        #print "len(line)=" + `l`
        
        if (l > 0 and l <= 3) :	# caused by AMUN logs - need to fix at source but this adds some protection
            msg = "kojoney_tweet_engine.py : Short line read, len=" + `l` + " so ignore..."
            print msg
            syslog.syslog(msg)
        elif not line :		# no data to process
            #print "kojoney_tweet_engine.py : nothing in Tweets queue to process"          
            file.seek(where)
        else:
            print "kojoney_tweet_engine.py : read entry from Tweet queue=" + line                    
            tweet = line.split("tweet=")[1]
            tweet = tweet.strip('"')
            print "**** kojoney_tweet_engine.py tweet=" + tweet

            # Filter out events that can't be correlated
            if suppressTweet(tweet) == None :
                print "kojoney_tweet_engine.py : suppress Tweet : " + tweet
                continue			# go back to top of loop
                                    
            # Perform basic event correlation here -> do not Tweet if correlation occurs
            count = 5
            a = kojoney_correlate.correlate(tweet,count)
            if a == 0 :
                tweet = "<" + `a` + ">" + tweet		# <0> signifies Tweet is NOT subjected to correlation
            elif a == count : 				# [n] signifies last time this event will be uncorrelated, so signal by pre-pending *
                tweet = "[" + `a` + "]" + tweet
            elif a < count :
                tweet = "{" + `a` + "}" + tweet		# {n} signifies non-correlated Tweet
            
            if a > count :			
                #syslog.syslog("kojoney_tweet_engine.py : DROP_CORRELATED_TWEET : " + tweet)
                #print "kojoney_tweet_engine.py : drop correlated Tweet : " + tweet
                continue
                        
            if line.find("cmd=GEO_IP") != -1 :
                print "GEO_IP:" + tweet
                twitter_funcs.sendGeoIPTweet(tweet)
                syslog.syslog("SENDTWEET = " + tweet)
            elif line.find("cmd=BASIC") != -1 :
                print "BASIC:" + tweet
                twitter_funcs.sendTweet(tweet)
                syslog.syslog("SENDTWEET = " + tweet)
                
        time.sleep(3)		# use 3 secs

except Exception,e:
        
        print "kojoney_tweet_engine.py : main() exception caught = " + `e` + " line=" + line
        syslog.syslog("kojoney_tweet_engine.py : main() exception caught = " + `e` + " line=" + line)
