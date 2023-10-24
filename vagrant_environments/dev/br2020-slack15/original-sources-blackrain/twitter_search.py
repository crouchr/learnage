#!/usr/bin/python
# Use this to send a single Tweet from script files etc.

import sys
import tweepy
import time


# honeytweeter
# ------------
CONSUMER_KEY    = 'N4EpgHKzFe5tf6mqmYqJQ'
CONSUMER_SECRET = 'Vr7Mxg6GdwY70a4w29ClKCqaD5w4BI7gqWPd0G1ME'
ACCESS_KEY    = '19196850-M2WmOBV1voMyFixfBaIJtJ5ol2ntihTte1lCxxRda'
ACCESS_SECRET = '9kWZw7JYrtNcCGpwhYb2qIsGgSqG88cCCUjjcYMwoE'

# Twitter username = blackraintweets
#CONSUMER_KEY    = 'N41qzhrygLrmxVMUXQhg'
#CONSUMER_SECRET = 'Ad13vdyy5HIjBY3nsipddCrSGVeXUacIjCeyz4hjABo'
#ACCESS_KEY      = '293023517-Aab9pQEGzECrGGj8lLjGsIqnB6CSOQGXmnlx476W'
#ACCESS_SECRET   = 'ZmtLBKNHVlnzImahZbMUgegz0PBM9st1fx7FIngDA' 

# testaccountbus
# --------------
#CONSUMER_KEY    = 'rvBsnnAnwqfAIgJB0bBL2A'
#CONSUMER_SECRET = 'VWL0I9Gpkv2wykiFEyjaoCSZq12bSXdWdUhbZfU8k'
#ACCESS_KEY    = '315918150-DH171QGTb2KDzLbPrRuISilmcrxAAnPbIGfR3Xlu'
#ACCESS_SECRET = '9J9DH5swkb65FQGk29zRLgjOJsV9YAGfLeGSsbqXLhg'

# sundayonglebe
# -------------
#CONSUMER_KEY    = 'qbBpTzwakv1O8hWokUaSWQ'
#CONSUMER_SECRET = 'ghm2F4ijo0pHyo6C56gsdUxdGUqi0MF6zmfemcCQ'
#ACCESS_KEY    = '315918150-qOCxf67WKxTkhNkcZsDj3JGdJFD4dGu3eoxbKZQ'
#ACCESS_SECRET = 'tH0NB53odAGfrEQFp14fb2Kr4cHBPAnUwDhtCs9bU'
#GLEBE_LAT  = "51.41335"
#GLEBE_LONG = "-1.37685" 

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api=tweepy.API(auth)

#now = time.time()
#msg = time.asctime(time.localtime(now)) + " : " + sys.argv[1]
#print msg

#api.update_status(sys.argv[1],lat="51.6",long="43.6")

#for term in ["botnet","ddos","vodafone"]:
for term in ["tango down"]:
    public = api.search(term)
    for tweet in public:
        print "-----------------------------------"
        print tweet.from_user
        print tweet.from_user_id
        print tweet.text.encode('utf-8')
        
#print a.__str__()
#api.update_status(sys.argv[1],lat=GLEBE_LAT,long=GLEBE_LONG)



