#!/usr/bin/python

import tweepy

DR_CONSUMER_KEY    = '8sgWbFKOr3jeIzmKqjFXIQ'
DR_CONSUMER_SECRET = 'US6XbuRCD8Ef6mHot8ZwBGqbuaoouV2PZ4PNTE3hXYA'

DR_ACCESS_KEY    = '170203470-6Qz17nnc6oV3cYJpAdwEWqe6aI3fTfx7Wl1luHOF'
DR_ACCESS_SECRET = 'HIGZrtONkUHF8jgBLlcBKvcEeos9cK9cUdxyQee8M'

# Basic authentication
#auth = tweepy.BasicAuthHandler('honeydrone6','fuckfacebook')
#api_dr = tweepy.API(auth)

# OAuth authentication
auth = tweepy.OAuthHandler(DR_CONSUMER_KEY, DR_CONSUMER_SECRET)
auth.set_access_token(DR_ACCESS_KEY, DR_ACCESS_SECRET)
api_dr=tweepy.API(auth)


#print "\nPublic Timeline"
#public_timeline = api_dr.public_timeline()
#print [tweet.text for tweet in public_timeline]

print "\nhoneydrone6 Home Timeline"
home_timeline = api_dr.home_timeline()

for tweet in home_timeline:
    print "id=" + `tweet.id` + " text=" + tweet.text
    
#print [tweet.text for tweet in home_timeline]

#print "\nhoneydrone6 Friends Timeline"
#friends_timeline = api_dr.friends_timeline()
#print [tweet.text for tweet in friends_timeline]

                        