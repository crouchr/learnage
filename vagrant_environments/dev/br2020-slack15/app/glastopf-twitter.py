#!/usr/bin/python
import urllib
 
username = 'honeytweeter'
password = 'fuckfacebook' 
message = "Hello Twitter!" 
data = urllib.urlencode({"status" : message})
res = urllib.urlopen("http://%s:%s@twitter.com/statuses/update.xml" % (username,password), data)
