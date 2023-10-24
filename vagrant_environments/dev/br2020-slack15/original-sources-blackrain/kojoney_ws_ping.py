#!/usr/bin/python
#
# BlackRain
# 
# Script to send WS ping to the BRX every n seconds as a basic keep-alive mechanism
# Allows the BRX to measure the uptime of a sensor and indicate if a sensor has gone off-line
#

import urllib,urllib2,time

# Put this in an include at next stage
BaseURL = 'http://www.mooghill.com/rocknroll'
    
# This will be a commonly used function to retrieve the basic info sent in all POSTs from sensor to BRX    
# Tag = sensorVersion + sensorId + wanIP
def fillSensorTag(wsRequest):    
    wsRequest['sensorVersion']  = "1.0"
    wsRequest['sensorId']       = "00:23:32:CD:BE:EF"
    wsRequest['wanIP']          = "217.41.27.169"
    return wsRequest

# The BRX will send the keepalive value via WS
# Keepalive = period between wsPings() in seconds
# Keepalive will probably be set to something like 60 seconds, just using 5 for testing
def lookupKeepalive():
    return 5		# hard-code for the moment

# ping the BRX at WS application layer
# need to explicitly look for HTTP 200 OK - but need the BRX to implement this before can test
def wsPing():
    
    wsRequest  = {}
    wsRequest  = fillSensorTag(wsRequest)
    
    wsURL = BaseURL + '/stub_Ping.php'
    data = urllib.urlencode(wsRequest)
    
    try:
        response = urllib2.urlopen(wsURL,data)		# HTTP 1.1 POST according to tshark
        page = response.read()
        print page
        return True 

    except urllib2.URLError, e:
        if hasattr(e, 'code'):
            if e.code == 404:
                #print "Explicitly trapped exception"
                print e
                return False                                                                               
        else:
                print e
                return False                                        
                                                       
# Main loop
if __name__ == '__main__' :

    keepalive = lookupKeepalive()

    # sit in an infinite loop and send WS pings to the BRX 
    while True:
        result = wsPing()
        print "Result of wsPing is " + `result`
        print "\nsleeping for " + `keepalive` + " seconds..."
        time.sleep(keepalive)
        
        