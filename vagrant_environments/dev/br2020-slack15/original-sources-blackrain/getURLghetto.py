#!/usr/bin/python
import re


# return first URL found in string sometext
def getURLghetto(sometext):
    try:
        #print "sometext = " + sometext
        first = re.search("(?P<url>https?://[^\s]+)",sometext).group("url")
        return first
    except Exception,e:		# can't find a URL
        #syslog.syslog("kojoney_tail.py : alert() : " + `e` + " ip=" + ip)
        return None
        
if __name__ == '__main__' :
    myString = "This is my tweet check it out http://tinyurl.com/blah"
    a = getURLghetto(myString)
    print a

    myString = "This is my tweet check it out http://www.google.com/blah"
    a = getURLghetto(myString)
    print a

    myString = "This is my tweet check it out https://tinyurl.com/blah"
    a = getURLghetto(myString)
    print a
  


