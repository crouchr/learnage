#!/usr/bin/python
# test the caching behaviour of bit/ly wrapper from a script in a different file to the fn itself

import kojoney_bitly
    
print "\nTest case #1 : valid URL"
short = kojoney_bitly.getBitly("http:/www.google.com")
print "Short URL = " + short
                    
print "\nTest case #2 : valid URL cached #1"
short = kojoney_bitly.getBitly("http:/www.google.com")
print "Short URL = " + short
                     
print "\nTest case #3 : valid URL"
short = kojoney_bitly.getBitly("http:/www.cisco.com")
print "Short URL = " + short
                     
print "\nTest case #4 : cache still working ? #1 "
short = kojoney_bitly.getBitly("http:/www.google.com")
print "Short URL = " + short
                     
print "\nTest case #5 : cache still working ? #2"
short = kojoney_bitly.getBitly("http:/www.cisco.com")
print "Short URL = " + short
                                