#!/usr/bin/python
# Run this once per Twitter account to get ACCESS key and secret
# 
# Instructions
# -----------
# 1. Visit www.twitter.com/oauth_clients using standard browser
# 2. Login using your Twitter account
# 3. Register a new application

# 3.#  & receive CONSUMER key & secret
# 2. Copy CONSUMER key and secret into this script
# 3. Run this script to receive ACCESS key & secret
# 4. Note all 4 variables, they are all needed for Twitter API

#root@mars:/home/crouchr# ./tweepy_auth.py
#CONSUMER_KEY    = '%s'N41qzhrygLrmxVMUXQhg
#CONSUMER_SECRET = '%s'Ad13vdyy5HIjBY3nsipddCrSGVeXUacIjCeyz4hjABo
#Please authorise by visiting the following URL using a GUI browser : 
#http://twitter.com/oauth/authorize?oauth_token=MfkPZJefRfJ6eTlqvgpceWIOmi4cH2z6BhZswZuIvDY
#PIN: 3848207
#ACCESS_KEY    = '293023517-Aab9pQEGzECrGGj8lLjGsIqnB6CSOQGXmnlx476W'
#ACCESS_SECRET = 'ZmtLBKNHVlnzImahZbMUgegz0PBM9st1fx7FIngDA'
#root@mars:/home/crouchr# 
 
import tweepy

# honeytweeter
# ------------
# read/write access
#CONSUMER_KEY    = 'N4EpgHKzFe5tf6mqmYqJQ'
#CONSUMER_SECRET = 'Vr7Mxg6GdwY70a4w29ClKCqaD5w4BI7gqWPd0G1ME'

# honeycc6
# --------
# read/write access
#CONSUMER_KEY    = '33x5LddMg3qzsP5TuNfLfA'
#CONSUMER_SECRET = 'U7HE8dF9apM97WKNCFDQrZVaH5VJukNhHYv6QLTEM'
#ACCESS_KEY      = '315918150-DOOljxmEkXxt5s7ILblJfAvUFN20MDHcjY5vV7rB'
#ACCESS_SECRET   = 'zqZBQYR6lEcVFFt9ZmBkJ37YIY6LrJmCGGvN8Lopg'

# honeydrone6
# -----------
# read-only access
#CONSUMER_KEY    = '8sgWbFKOr3jeIzmKqjFXIQ'
#CONSUMER_SECRET = 'US6XbuRCD8Ef6mHot8ZwBGqbuaoouV2PZ4PNTE3hXYA'

# ----------

# testaccountbus
# --------------
#CONSUMER_KEY    = 'qbBpTzwakv1O8hWokUaSWQ'
#CONSUMER_SECRET = 'ghm2F4ijo0pHyo6C56gsdUxdGUqi0MF6zmfemcCQ'
#ACCESS_KEY    = '315918150-qOCxf67WKxTkhNkcZsDj3JGdJFD4dGu3eoxbKZQ'
#ACCESS_SECRET = 'tH0NB53odAGfrEQFp14fb2Kr4cHBPAnUwDhtCs9bU'

# sundayonglebe / stockcross
# --------------------------
#CONSUMER_KEY    = 'g0dQDXL14QLw3PrVhPquA'
#CONSUMER_SECRET = 'IjzwuWqmteO3adxihh4aWXN6RABjHK7jle57HsOfwg'
#ACCESS_KEY      = '304481178-Cl1eBSrBAFZ69dUUPFrujUkV5UsmShB3UjcAX7PB'
#ACCESS_SECRET   = '0fMhp1NX2DMDbKqxO6h2aTZqEWGmQAIQr6ijRQoIak'

# blackraintweets
# ---------------
#CONSUMER_KEY = 'N41qzhrygLrmxVMUXQhg'
#CONSUMER_SECRET = 'Ad13vdyy5HIjBY3nsipddCrSGVeXUacIjCeyz4hjABo'
#ACCESS_KEY    = '293023517-Aab9pQEGzECrGGj8lLjGsIqnB6CSOQGXmnlx476W'
#ACCESS_SECRET = 'ZmtLBKNHVlnzImahZbMUgegz0PBM9st1fx7FIngDA'

# @Synapsile
# ----------
CONSUMER_KEY    = 'p8GgD6KNUwOpjJYNiBI0OvXIF'
CONSUMER_SECRET = 'vmcVKiwfFJ703cTPEOfNZyH3dkVPd6ebOwQdt9pe9Eapmq86t0'
ACCESS_KEY      = '2815408698-0z4yiKmXv27bHwgDwfXmA13mTbTzBRQ03OvtDTH'
ACCESS_SECRET   = 'DlKAnAecLLO96MvcvLnc971ripUW0K92TchZ2kRcxb7rX'

try :
    print "CONSUMER_KEY    = " + CONSUMER_KEY
    print "CONSUMER_SECRET = " + CONSUMER_SECRET

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth_url = auth.get_authorization_url()
    print 'Please authorise by visiting the following URL using a GUI browser : \n' + auth_url
    verifier = raw_input('PIN: ').strip()
    auth.get_access_token(verifier)

    print "ACCESS_KEY    = " + auth.access_token.key
    print "ACCESS_SECRET = " + auth.access_token.secret
except Exception,e:
    print "Failure : " + e.__str__()
    
