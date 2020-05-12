#!/usr/bin/python
# simple test of Python API
import twitter
import time

print "Started"
msg = "ignore : this is a test message : id = " + `time.time()`

print "Send tweet via Twitter"
client = twitter.Api(username="honeytweeter",password="fuckfacebook")
status = client.PostUpdate(msg)
print "Status of update is " + `status`

#print "Send tweet via identi.ca"
#client = twitter.Api(username="honeytweeter",password="fuckfacebook",base_url='http://identi.ca/api')
#status = client.PostUpdate(msg)
#twitter.Api(..., base_url='http://identi.ca/api')