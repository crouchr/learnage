#!/usr/bin/python
# Use this to send a single Tweet from script files etc.

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

# honeycc
# =======

GLEBE_LAT  = "51.41335"
GLEBE_LONG = "-1.37685" 

MaxTweetLen = 140 - 16

SecsInADay  = 3600 * 24		# period between Tweets
SecsInADay  = 3600		# period between Tweets : value for testing

JitterMins  = 30		# add upto this number of minutes to the send time so it doesn't look like a machine
JitterMins  = 5			# value for testing

OpsTwitter  = "honeycc6"
MainTwitter = "testaccountbus"

#
#
def sendTweet(username,tweet):
    global MaxTweetLen

    try:    
        time.sleep(2)
    
        now = time.time()
        #print "now = " + now.__str__()

        # Add now to tweet so it is always unique
        #if username == OpsTwitter :
        tweet = "id=" + now.__str__() + ":" + tweet
        print username
        
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
        elif username == 'honeycc6' :    
            CONSUMER_KEY    = '33x5LddMg3qzsP5TuNfLfA'
            CONSUMER_SECRET = 'U7HE8dF9apM97WKNCFDQrZVaH5VJukNhHYv6QLTEM'
            ACCESS_KEY      = '315918150-DOOljxmEkXxt5s7ILblJfAvUFN20MDHcjY5vV7rB'
            ACCESS_SECRET   = 'zqZBQYR6lEcVFFt9ZmBkJ37YIY6LrJmCGGvN8Lopg'
        
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
        
    tweets = []
    
    now = time.time()
    print now
    print time.asctime(time.localtime(now))
    print "MaxTweetLen is " + MaxTweetLen.__str__()
    
    # Calculate epoch of the event : 15:00 July 10th 2011
    event = (2011,7,10,15,0,0,-1,-1,True) 
    event = (2011,6,13,15,00,0,-1,-1,True) 
    eventEpoch = time.mktime(event)
    print "eventEpoch = " + eventEpoch.__str__()
    print time.localtime(eventEpoch)
    print time.asctime(time.localtime(eventEpoch))
    
    # Calculate when to start Tweeting : 1 pm
    campaignStart = (2011,6,13,3,0,0,-1,-1,True) 
    campaignEpoch = time.mktime(campaignStart)
    print "campaignEpoch = " + campaignEpoch.__str__()
    print time.localtime(campaignEpoch)
    print time.asctime(time.localtime(campaignEpoch))

    if campaignEpoch >= eventEpoch :
        print "Invalid epoch times, exiting..."
        sys.exit()
  
    # Fill list with tweets to be sent
    for line in fileinput.input("sotg-tweets.txt"):
        line = line.strip()        
        a = len(line)
        #print "Length of tweet = " + a.__str__()
        
        # Ignore comments at start of line
        if line[0] == "#" : 
            continue
        if a <= MaxTweetLen:
            tweets.append(line)
            print "Tweet added OK : " + line
        else:
            print "Error : len=" + a.__str__() + " for tweet=" + line
    # print tweets    

    numOfTweets = len(tweets)
    print "Number of valid tweets  = " + numOfTweets.__str__()

    secsTillCampaign = campaignEpoch - now
    print "Number of seconds until automated Twitter campaign starts is " + secsTillCampaign.__str__()
    print "Waiting..."
    time.sleep(secsTillCampaign)
        
    while True:
        for tweet in tweets:
            print "-----------------------------------------"
            i = tweets.index(tweet)
            msg = "SOTG_OPS : Current tweet index = " + i.__str__()
            print msg
            
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
                #print "Jitter (in seconds) is " + jitter.__str__() + " i.e. " + str(jitter/60) + " minutes" 
                timeToWait = SecsInADay + jitter
                
                msg = "SOTG_OPS : Current tweet index = " + i.__str__() + ", number of seconds until next Tweet is sent = " + timeToWait.__str__()
                syslog.syslog(msg)
                #sendTweet(OpsTwitter,msg)
                
                msg = "SOTG_OPS : countdownSecs = " + countdownSecs.__str__()
                #sendTweet(OpsTwitter,msg)
                syslog.syslog(msg)
                
                # Work out what the next tweet will be 
                x = (i+1) % 12
                #print "x = " + x.__str__()
                msg = "SOTG_OPS : Next Tweet = " + tweets[x]
                #print msg
                #sendTweet(OpsTwitter,msg)
                syslog.syslog(msg)
                
                print "Waiting..."
                time.sleep(timeToWait)
                #time.sleep(1)
            
                
            
            
        print " "
        print "===================================================="
        print "=                    Next cycle                    ="
        print "===================================================="
        print " "
            
        #tweet(line)
        #time.sleep(60)
        #time.sleep(5)

if __name__ == "__main__" :
    main()