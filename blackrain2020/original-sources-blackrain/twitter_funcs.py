#!/usr/bin/python

import time, os , syslog , re , sys 

import tweepy
from tweepy.error import TweepError

import ipintellib	# RCH library

TweetId = 0		# increment so each Tweet is not the same - Twitter API rejects identical ones in same 24 hours

# this is the function that applications should use 

def addTweetToQueue(tweet,geoip=False,tstamp=None):
    try:
        if geoip == True :
            cmd = "GEO_IP"
        else:
            cmd = "BASIC"

        tweet = tweet.rstrip("\n")	# ensure no trailing newline characters
                
        now = time.time()
        tuple=time.localtime(now)
        timestamp = "%02d" % tuple.tm_hour + ":" + "%02d" % tuple.tm_min    
         
        if tstamp == None:
            tweet = tweet  
        else:      			# prepend a minimal localtime timestamp : HHMM
            tweet = timestamp + "," + tweet
        
        #tweet = '"' + tweet + '"'
        msg = "submitted=" + time.asctime(tuple) + " cmd=" + cmd + " tweet=" + tweet      
        fpOut = open(r'/home/var/log/tweet_queue.log','a')
        print >> fpOut,msg 
        fpOut.close()
        print "twitter_funcs.py : added entry to Tweet queue :" + msg
        
    except Exception,e:
        syslog.syslog("twitter_funcs.py : addTweetToQueue() exception caught = " + `e` + " tweet=" + tweet)

# Wrapper
# Extract first non-honeypot IP from a Tweet
# Perform GeoIP on IP to get lat/long
# Call SendTweet() to send the Tweet
# Assumes that Tweet has had honeypot IPs converted to text not IP addresses
def sendGeoIPTweet(tweet_raw) :
    try :
        latitude  = None
        longitude = None
        tweet = tweet_raw
        metaData = None
        
        pat = r'\d+\.\d+\.\d+\.\d+'             # locate a number of IP addresses
        ips = re.findall(pat,tweet)     
        if len(ips) != 0 :
            ip = ips[0]
 
            # GeoIP information - faster than WHOIS for looking up Country Code information
            geoIP = ipintellib.geo_ip(ip)                                
            countryCode = geoIP['countryCode']                              
            city        = geoIP['city']
            longitude   = geoIP['longitude']                                # Used to calc approx. localtime
            latitude    = geoIP['latitude']        
            metaData = "city=" + city + " cc=" + countryCode 
            
            if countryCode == 'None':
                tweet = "??" + "," + tweet_raw
            else:
                tweet = countryCode + "," + tweet_raw
        else: # Did not find an IP address
            tweet = "--" + "," + tweet_raw        
        
        sendTweet(tweet,lat=latitude,long=longitude,meta=metaData)
    
    except Exception,e:
        syslog.syslog("twitter_funcs.py : sendGeoIPTweet() exception caught = " + `e` + " tweet_raw=" + tweet_raw)

# locate Tweets of Interest
# put to file initially and then to a separate Twitter channel
# multiple file entries per Tweet are possible
def tweetsOfInterest(tweet):

    try :
        # syslog.syslog("twitter_funcs.py : entered tweetOfInterest() " + tweet)
        # keywords MUST be all lower-case
        # note the use of padding spaces for words that a common subsets of non-interesting words
        keywords = [" cisco ","netgear","router","webcam","printer","firewall","newbury","openwrt",\
        " ios ","freebsd","sunos","openbsd","juniper","junos","screenos","netscreen",\
        "vpn","anon","wifi","voip","gprs","wireless","mod_","pastebin",\
        "portscan detected","flood","exploit","malware","infection","vulnerability","sandbox","shellcode","eggdrop","proxy","psybnc","irc","bruteforce",\
        "mw-found","user-agent","tool","bot","trojan","backdoor","blacklist"," dos ","denial","noop","cmd.exe","w00t"," root ","passwd",\
        "sasser","worm","RBN Host",\
        "blackhat","security","w00t",\
        "Microsoft SQL Server",\
        "select","union",\
        "amazonaws.com","vps",\
        "os=IOS",\
        "sJUICE",\
        "blackhole",\
        "kippo","anubis",\
        "prolexic","VODANET","vf-vodanet","vodafone","as25135","as3209","as30722","DTAG","as3269"]
        
        for i in keywords :
            #tweetLower = tweet.lower()
            #print tweetLower
            if tweet.lower().find(i.lower()) != -1 : 
                msg = i + "," + tweet
                fpOut = open(r'/home/var/log/tweetsofinterest.txt','a')
                print >> fpOut,msg 
                fpOut.close()
                #print msg
                #syslog.syslog("twitter_funcs.py : tweetsOfInterest() : " + msg)
        
    except Exception,e:
        syslog.syslog("twitter_funcs.py : tweetsOfInterest() exception caught = " + `e` + " tweet=" + tweet)


# Look for multiple IPs in a Tweet and then obfuscate them
# Do not obfuscate routes i.e. 3.4.5.0/24
def anonymizeIP(msg):

    try :
        #syslog.syslog("twitter_funcs.py : entered anonymizeIP() : " + msg)

        # Stage 1 - replace IP addresses        
        pat = r'\d+\.\d+\.\d+\.\d+'             # locate a number of IP addresses
        ips = re.findall(pat,msg)     
        
        if len(ips) != 0 :	# found 1 or more IP addresses
            #ip = ips[0]
            
            #a = "anonymizeIP : ip found = " + ip 
            #syslog.syslog(a)
            #print a
            print ips
            for ip in ips:
                print ip
                #if ip.find("/") != -1 :	# this is a route so do not obfuscate
                #    print ip + " is a route, so do not obfuscate"
                #    continue		# go to next IP in list
                octets = ip.split(".")
                lastOctet = octets[3]
                #anonIP = octets[0] + "." + octets[1] + "." + octets[2] + "." + "xxx"
                anonIP = octets[0] + "." + octets[1] + "." + octets[2] + "." + "x"
                #a = "anonymizeIP : anonIP = " + anonIP
                #syslog.syslog(a)
                #print a
            
                msg = msg.replace(ip,anonIP)
        
        # Stage 2 - replace DNS names         
        # e.g. 123-12-32-32.adsl.com -> x-x-x-x.adsl.com
        pat = r'\d+\-\d+\-\d+\-\d+'	# locate a number of DNS names 
        ips = re.findall(pat,msg)     
        
        if len(ips) != 0 :	# found 1 or more IP addresses
            #ip = ips[0]
            
            #a = "anonymizeIP : ip found = " + ip 
            #syslog.syslog(a)
            #print a
            
            print ips
            for ip in ips:
                print ip
                octets = ip.split("-")
                anonIP = "x-x-x-x"
                #a = "anonymizeIP : anonIP = " + anonIP
                #syslog.syslog(a)
                #print a
            
                msg = msg.replace(ip,anonIP)
            
            a = "twitter_funcs.py : anonymized Tweet -> " + msg
            #syslog.syslog(a)
            #print a            
            return msg
        else:			# did not find an IP
            #a = "twitter_funcs.py : anonymizeIP() : no IP found in " + msg
            #syslog.syslog(a)
            return msg    

    except Exception,e:
        syslog.syslog("twitter_funcs.py : anonymizeIP() exception caught = " + `e` + " tweet_raw=" + msg)


# --------------------------------------

# wrapper for sending Tweets
# comment out line status=... to disable actual Twitter API call during testing
# add support for selecting the account to use
# meta = whatever cvs info to append to the Tweet log (does not get tweeted)
# tweet = tweet[:::]
# inband parameter : if ":::" is present (at the end of the tweet) then do not send the tweet via the API, only log it

def sendTweet(tweet_raw,lat=None,long=None,meta=None,account="honeytweeter"):
    global TweetClient
    global TweetId
    
    if tweet_raw == None:
        return
    tweet_raw = tweet_raw.strip('"')	# strip enclosing "
    tweet_raw = tweet_raw.rstrip("\n")	# Ensure no trailing \n characters
    
#    MAXTWEET_LEN = 137			# max chars to send
    MAXTWEET_LEN = 120			# max chars to send
    
    now = time.time()
    
    ####print "twitter_funcs.py : sendTweet() entered function, tweet_raw = " + tweet_raw + ", lat=" + `lat` + " long=" + `long`
    #print "twitter_funcs.py : sendTweet() entered function, tweet_raw = " + tweet_raw 

    if account == "honeytweeter" :
        CONSUMER_KEY    = 'N4EpgHKzFe5tf6mqmYqJQ'
        CONSUMER_SECRET = 'Vr7Mxg6GdwY70a4w29ClKCqaD5w4BI7gqWPd0G1ME'
    
        ACCESS_KEY      = '19196850-M2WmOBV1voMyFixfBaIJtJ5ol2ntihTte1lCxxRda'
        ACCESS_SECRET   = '9kWZw7JYrtNcCGpwhYb2qIsGgSqG88cCCUjjcYMwoE'
    else:
        return
         
    try:
        if (lat != None and long != None) :
            lat  = '%.2f' % lat	    # truncate to 2 decimal points as required by Twitter
            long = '%.2f' % long    # truncate to 2 decimal points as required by Twitter
        
        #print "sendTweet() : after truncation to 2 decimal points, lat=" + `lat` + " long=" + `long` 
        
        # If GeoIP failed, then set to None so as not to have Tweepy reject the API call - hypothesis at the moment
        if lat == '999.00' or long == '999.00' :
            #print "send_tweet() : no geoip information obtained"
            lat = None
            long = None
        
        # Low-level override of anything performed by crouchr account
        tweet = tweet_raw.replace("crouchr"   , "***")			# AAA logs for router login
        tweet = tweet_raw.replace("s0lab0sch" , "***")			# 
        tweet = tweet_raw.replace("trisfmotp" , "***")			# 
    
    
        # Add tweet - before anonymisation / truncation etc. to a file purely for visualisation
        msg = tweet  
        fpOut = open(r'/home/var/log/tweets.visualistion.txt','a')
        print >> fpOut,msg 
        fpOut.close()
    
        # prepend TweetId to prevent duplicate Tweets and to check how reliable the tweet API is 
        TweetId = TweetId + 1 
        tweet = "#hnytwtr" + " " + "id" + `TweetId` + "," + tweet
        
        # search for keywords in Tweet and save to a file
        # Note - this is done *before* anonymization and before truncation
        tweetsOfInterest(tweet)
            
        # prepend a minimal localtime timestamp : HHMM   
        #tuple=time.localtime(now)
        #timestamp = "%02d" % tuple.tm_hour + ":" + "%02d" % tuple.tm_min    
        #tweet = timestamp + "," + tweet
      
        # obfuscate the IP addresses
        tweet = anonymizeIP(tweet)
      
        # truncate (concatenate in future ?) long tweets 
        if len(tweet) >= MAXTWEET_LEN:
            tweet=tweet[0:MAXTWEET_LEN]
            tweet=tweet + "..."				# + indicates tweet was truncated
        else:     
            pass
                
        # Log all attempts to send Tweets - before using the API (in case the Twitter API fails)
        
        if meta != None:
            metaData = "," + meta
        else:
            metaData = ""    
        msg = "[" + tweet + "]" + " metadata:lat=" + `lat` + "," + "long=" + `long` + metaData 
        #print msg

        msg = `TweetId` + "," + msg
        fpOut = open(r'/home/var/log/tweets.attempts.log.txt','a')
        print >> fpOut,msg 
        fpOut.close()
        

        # ******************************************************************************************
        # actually send the Tweet - here is where you disable Tweeting during testing
        # You need to enable the Tweet account for geotagging under Settings tab on Twitter Web page        
        # ******************************************************************************************     

        print "*** twitter_funcs.py : sendTweet() sent by API : tweet = " + msg
        if tweet.find(":::") == -1 :	# ":::" at end of tweet == do not tweet via API
            #syslog.syslog("twitter_funcs.py : sendTweet() : TWITTER_API : " + tweet)
            start = time.time()
            auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
            auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
            api = tweepy.API(auth)
            api.update_status(tweet,lat=lat,long=long)
            end = time.time()
            
            # Calculate duration of Twitter submission
            apiTime = end - start
            #syslog.syslog("twitter_funcs.py : sendTweet() : Tweet sent OK : TWITTER_PERF : " + "%.2f" % apiTime + " secs")
            
            fpOut = open(r'/home/var/log/tweets.sent.log.txt','a')
            print >> fpOut,msg,apiTime.__str__() 
            fpOut.close()
    
            time.sleep(5)	# crude rate limit into Twitter 
    
    # Trap Twitter exceptions
    except Exception,tweepy.TweepError:
        msg = "twitter_funcs.py : sendTweet() exception : TweepError = [" + tweepy.TweepError.__str__() + "], length of tweet = " + len(tweet).__str__()
        print msg
        syslog.syslog(msg)
        
        fpOut = open(r'/home/var/log/tweepError.txt','a')
        msg = "twitter_funcs.py : sendTweet() exception : TweepError = [" + tweepy.TweepError.__str__() + "], length of tweet = " + len(tweet).__str__() + ", tweet=" + tweet.__str__()
        print >> fpOut,msg
        fpOut.close()
    
        msg = "twitter_funcs.py : sendTweet() exception : tweet = " + tweet.__str__()
        print msg
        syslog.syslog(msg)
        
        return
        #return False,tweepy.TweepError.__str__()
        
    # Trap general exceptions                             
    except Exception,e:
        syslog.syslog("twitter_funcs.py : sendTweet() : exception caught = " + `e` + " tweet_raw=" + tweet_raw)


if __name__ == '__main__' :

    tweet = "Here is an attack from 1.2.3.4:43 that needs to be anonymised"
    print tweet
    tweet = anonymizeIP(tweet)
    print tweet
    print " "
    
    tweet = "Here is an attack from 1.2.3.4:43 towards 4.5.6.7 that needs to be anonymised"
    print tweet
    tweet = anonymizeIP(tweet)
    print tweet
    print " "
    
    tweet = "Here is an attack from 1.2.3.4:43 using route 34.56.2.0/24 that needs to be anonymised"
    print tweet
    tweet = anonymizeIP(tweet)
    print tweet
    print " "
    
    tweet = "Here is an attack from 1-2-3-4.dynamic.adsl.com towards 4.5.6.7 that needs to be anonymised"
    print tweet
    tweet = anonymizeIP(tweet)
    print tweet
    print " "
    
    tweet = "Here is an attack with no IP address that needs to be anonymised"
    print tweet
    tweet = anonymizeIP(tweet)
    print tweet
    print " "

    tweet = "Here is a Tweet with Cisco router from AS3209 and Vodafone in it - with a trojanised piece of bot shellcode from an IRC proxy"
    tweetsOfInterest(tweet)

#    tweet = "twitter_funcs.py : Here is a test Tweet"
#    sendTweet(tweet,account="honeytweeter")
                                                                                                      