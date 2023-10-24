#!/usr/bin/python
# Use this to send a single Tweet from script files etc.
# Master is on mail

import sys
import tweepy
import fileinput
import time
import syslog
from random import randrange

# testaccountbus
# ==============
#CONSUMER_KEY    = 'qbBpTzwakv1O8hWokUaSWQ'
#CONSUMER_SECRET = 'ghm2F4ijo0pHyo6C56gsdUxdGUqi0MF6zmfemcCQ'
#ACCESS_KEY      = '315918150-qOCxf67WKxTkhNkcZsDj3JGdJFD4dGu3eoxbKZQ'
#ACCESS_SECRET   = 'tH0NB53odAGfrEQFp14fb2Kr4cHBPAnUwDhtCs9bU'


TEST = True	# add id to tweet so that they are all unique

GLEBE_LAT  = "51.41335"
GLEBE_LONG = "-1.37685" 

MaxTweetLen = 140 - 16

SecsInADay  = 3600 * 24		# period between Tweets
SecsInADay  = 3600		# period between Tweets : value for testing

JitterMins  = 30		# add upto this number of minutes to the send time so it doesn't look like a machine
JitterMins  = 5			# value for testing

#OpsTwitter  = "honeycc6"
MainTwitter = "testaccountbus"

#
#
def sendTweet(username,tweet):
    global MaxTweetLen
    global TEST

    try :    
        time.sleep(2)
        now = time.time()
        #print "now = " + now.__str__()

        # Add now to tweet so it is always unique
        #if username == OpsTwitter :
        if TEST == True:
            tweet = "id=" + now.__str__() + ":" + tweet
        
        a = len(tweet)
        print "Length of Tweet is " + a.__str__()
        if (a > MaxTweetLen):
           msg = "Truncated Tweet : Tweet too long, it is " + a.__str__() + " characters long, MaxTweetLen is " + MaxTweetLen.__str__() 
           print msg
           print tweet
           tweet = tweet[:156] + "..."
       
       #return False 
    
        # Actually send the Tweet   
        if username == "testaccountbus" :
            CONSUMER_KEY    = 'qbBpTzwakv1O8hWokUaSWQ'
            CONSUMER_SECRET = 'ghm2F4ijo0pHyo6C56gsdUxdGUqi0MF6zmfemcCQ'
            ACCESS_KEY      = '315918150-qOCxf67WKxTkhNkcZsDj3JGdJFD4dGu3eoxbKZQ'
            ACCESS_SECRET   = 'tH0NB53odAGfrEQFp14fb2Kr4cHBPAnUwDhtCs9bU'
 #       elif username == 'honeycc6' :    
 #           CONSUMER_KEY    = '33x5LddMg3qzsP5TuNfLfA'
 #           CONSUMER_SECRET = 'U7HE8dF9apM97WKNCFDQrZVaH5VJukNhHYv6QLTEM'
 #           ACCESS_KEY      = '315918150-DOOljxmEkXxt5s7ILblJfAvUFN20MDHcjY5vV7rB'
 #           ACCESS_SECRET   = 'zqZBQYR6lEcVFFt9ZmBkJ37YIY6LrJmCGGvN8Lopg'
        
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
        api = tweepy.API(auth)
        api.update_status(tweet,lat=GLEBE_LAT,long=GLEBE_LONG)    
        print "*** Tweet sent to " + username + " ::: [" + tweet + "]"
        syslog.syslog("Tweeted to " + username + ":" + tweet)
    except Exception,e:
        syslog.syslog("sendTweet() exception = " + e.__str__())
        return False
        
    return True

#
#
def main():
    global MaxTweetLen
    global OpsTwitter, MainTwitter
    global TEST
    try :        
        tweets = []
        
        syslog.openlog("autotweetr")
        syslog.syslog("autotweetr started, TEST=" + TEST.__str__())

        print "argc = " + len(sys.argv).__str__()
        
        if len(sys.argv) != 2 :
            msg = "Abort : You need to specify the file to read Tweets from as the first command line argument"
            syslog.syslog(msg)
            print msg
            sys.exit()
        else :
            tweetFile = sys.argv[1]
            print "tweetFile is " + tweetFile.__str__()
            syslog.syslog("Read Tweets from " + tweetFile.__str__())
        
        now = time.time()
        print now
        print time.asctime(time.localtime(now))
        print "MaxTweetLen is " + MaxTweetLen.__str__()
    
        # Calculate epoch of the event : 15:00 July 10th 2011
        event = (2011,7,10,15,0,0,-1,-1,True)   	# Real Thing
        #event = (2011,6,13,15,00,0,-1,-1,True)		# Test 
        eventEpoch = time.mktime(event)
        print "eventEpoch = " + eventEpoch.__str__()
        print time.localtime(eventEpoch)
        msg = "Stockcross event starts at : " + time.asctime(time.localtime(eventEpoch)).__str__()
        print msg
        syslog.syslog(msg)
    
        # Calculate when to start Tweeting : 1 pm
        # year month day hour minutes ...
        campaignStart = (2011,6,13,13,0,0,-1,-1,True)    # RealThing
        campaignStart = (2011,6,17,3,0,0,-1,-1,True)     # Test 
        campaignEpoch = time.mktime(campaignStart)
        print "campaignEpoch = " + campaignEpoch.__str__()
        print time.localtime(campaignEpoch)
        print time.asctime(time.localtime(campaignEpoch))
        msg = "Twitter campaign starts at : " + time.asctime(time.localtime(campaignEpoch)).__str__()
        print msg
        syslog.syslog(msg)
    
        if campaignEpoch >= eventEpoch :
            msg = "Invalid epoch times, exiting..."
            print msg
            syslog.syslog(msg)
            sys.exit()
  
        # Fill list with tweets to be sent
        for line in fileinput.input(tweetFile):
            line = line.strip()        
            a = len(line)
            #print "Length of tweet = " + a.__str__()
        
            # Ignore comments at start of line
            if line[0] == "#" : 
                continue
            if a <= MaxTweetLen :
                tweets.append(line)
                msg = "OK : " + line
                syslog.syslog(msg)
                print msg
            else :
                msg = "** Error : len=" + a.__str__() + " : " + line
                syslog.syslog(msg)
                print msg
                sys.exit()
    
        print "Tweets to be sent : \n" + tweets.__str__()

        numOfTweets = len(tweets)
        msg = "Number of valid tweets  = " + numOfTweets.__str__()
        print msg
        syslog.syslog(msg)

        msg = "Interval between Tweets is " + int(SecsInADay/3600).__str__() + " hour(s)"
        print msg
        syslog.syslog(msg)
    
        msg = "Jitter added to Interval is " + JitterMins.__str__() + " minute(s)"
        print msg
        syslog.syslog(msg)
    
        secsTillCampaign = campaignEpoch - now
        # duplicate reporting
        #msg = "Number of seconds until automated Twitter campaign starts is " + secsTillCampaign.__str__()
        #print msg
        #syslog.syslog(msg)
    
        msg = "Waiting for " + int(secsTillCampaign/3600).__str__() + " hours (="  + secsTillCampaign.__str__() + " seconds) until Twitter campaign starts..."
        print msg
        syslog.syslog(msg)
        time.sleep(secsTillCampaign)
        
        while True:
            for tweet in tweets:
                print "-----------------------------------------"
                i = tweets.index(tweet)
                msg = "SOTG_OPS : Current tweet index = " + i.__str__()
                print msg
                syslog.syslog(msg)
            
                # Send Tweet
                if sendTweet(MainTwitter,tweet) == True:
                    time.sleep(10)
                    now = time.time()
                    countdownSecs = eventEpoch - now
                
                    if countdownSecs <= 0 :
                        sendTweet(OpsTwitter,"SOTG_OPS : stockfest_tweeter exiting, the event has now started")
                        sys.exit()
                    else:
                        daysToGo  = int(countdownSecs/(24 * 3600))
                        hoursToGo = countdownSecs - (daysToGo * (24 * 3600))
                        hoursToGo = hoursToGo / 3600
                        #hoursToGo = hoursToGo - 1
                        msg = "Countdown to SOTG : Only " + daysToGo.__str__() + " day(s) & " + int(hoursToGo).__str__() + " hour(s) to go..."
                        sendTweet(MainTwitter,msg)
                
                    jitter = randrange(JitterMins * 60)
                    msg = "Jitter (in seconds) is " + jitter.__str__() + " i.e. " + str(jitter/60) + " minutes" 
                    print msg
                    syslog.syslog(msg)
                    timeToWait = SecsInADay + jitter
                
                    #msg = "SOTG_OPS : Current tweet index = " + i.__str__() + ", number of seconds until next Tweet is sent = " + timeToWait.__str__()
                    #syslog.syslog(msg)
                    #sendTweet(OpsTwitter,msg)
                
                    msg = "SOTG_OPS : countdownSecs = " + countdownSecs.__str__()
                    #sendTweet(OpsTwitter,msg)
                    syslog.syslog(msg)
                
                    # Work out what the next tweet will be 
                    x = (i+1) % numOfTweets
                    #x = (i+1) % 12
                    #print "x = " + x.__str__()
                    msg = "SOTG_OPS : Next Tweet = " + tweets[x]
                    #print msg
                    #sendTweet(OpsTwitter,msg)
                    syslog.syslog(msg)
                
                    msg = "Waiting for " + timeToWait.__str__() + " second(s) until next Tweet shall be sent..."
                    print msg
                    syslog.syslog(msg)
                    time.sleep(timeToWait)
                    #time.sleep(1)
                
            print " "
            print "===================================================="
            print "=                    Next cycle                    ="
            print "===================================================="
            print " "
            syslog.syslog("Repeating Tweets...")
    
    except Exception,e:
        msg = "Exception in autotweetr : " + e.__str__()
        print msg
        syslog.syslog(msg)
    
    

            
if __name__ == "__main__" :
    main()