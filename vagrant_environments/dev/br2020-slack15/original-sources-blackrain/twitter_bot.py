#!/usr/bin/python


import time, os , syslog , re 
import twitter		# Google API
from urlparse import urlparse

import codecs, sys
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

import ipintellib	# RCH library - master on mars
import mailalert	# RCH library
import p0fcmd		# RCH library - master on mars
import filter_sebek     # RCH library - master on mars
import extract_url      # RCH library - master on mars

#Twitter Timeline for @honeycc6 (C&C feed) :
#<a href="http://twitter.com/" rel="nofollow">Twitter for iPhone</a> ++ 19401136439L ++ 1279951738 ++ Gfftdchg
#<a href="http://twitter.com/" rel="nofollow">Twitter for iPhone</a> ++ 19400414178L ++ 1279950906 ++ Poweroff
#<a href="http://twitter.com/" rel="nofollow">Twitter for iPhone</a> ++ 19400322790L ++ 1279950799 ++ Rebbot
#web ++ 19398871393L ++ 1279949176 ++ test from honeycc6


def processCandCTweet(tweet) :
    print "processC&Ctweet() : raw tweet=" + tweet

# ==============
cache = {}

# Create a connection to Twitter
try:

#    TweetClient = twitter.Api(username="honeytweeter",password="fuckfacebook")                
    TweetClient = twitter.Api(username="honeydrone6",password="fuckfacebook")                

    #print "Twitter Public Timeline Status messages"
    #statuses = TweetClient.GetPublicTimeline()
    #print [s.user.name for s in statuses]
    #for s in statuses :
    #    print s.user.name

    # Populate cache for first time and do not process
    #statuses = TweetClient.GetUserTimeline("honeycc6")
    #for s in statuses : 
    #    cache[s.id] = s.text
    #    print s.text
    #print "Current Tweets added to stale cache"
    #print "Sleeping for 10 seconds..."
    #time.sleep(10)
    
    # Look for new tweets
    while True:
        #print "\nTwitter Public Timeline :"
        statuses = TweetClient.GetPublicTimeline()
        for s in statuses : 
            #print s.source + " ++ " + `s.user` + " +++ " + `s.id` + " ++ " + `s.created_at_in_seconds` + " ++ " + s.text       
            #print "tweet=" + s.text       
            if (s.text.find("ddos") != -1 or s.text.find("botnet") != -1 or s.text.find("cyberwarfare") != -1 or s.text.find("honeypot") != -1) : 
            #if (s.text.find("the") != -1) : 
                #print "***interesting content found***"
                msg = "@" + s.user.screen_name + "," + s.user.name + "," + s.user.description + "," + s.user.location + "," + s.text
                print msg
                time.sleep(1)
                
                #fileObj = codecs.open( "someFile", "r", "utf-8" )                
                f=codecs.open(r'/home/var/log/twitter_search.txt','a',"utf-8")
                print >> f,msg
                f.close()
                
        #print "Sleeping for 65 seconds..."
        time.sleep(65)
      
    print "Exiting."

except Exception,e:
    syslog.syslog("twitter_bot.py : exception " + `e`)
    
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
                              
                                                                 