#!/usr/bin/python
#
#
# http://www.mooghill.com/rocknroll/stub_DoSensorRegister.php?sensorId=00214365879A195123145001&SensorVersion=1.0&sensorBogomips=5667.35&baseIP=212155042002&sensorIP=192168001022
#
import os , syslog

import urllib
import urllib2
        
if __name__ == '__main__' :

    wsRequest  = {}
    wsResponse = {}
    
    wsRequest['sensorId']       = "00:23:32:CD:BE:EF"
    wsRequest['SensorVersion']  = "1.0"
    wsRequest['sensorBogomips'] = "2323.44"
    wsRequest['sensorIP']       = "217.41.27.169"
    wsRequest['baseIP']         = "192.168.1.55"

    url = 'http://www.mooghill.com/rocknroll/stub_DoSensorRegister.php'
    data = urllib.urlencode(wsRequest)
    response = urllib2.urlopen(url, data)
    page = response.read()
    
    print page    