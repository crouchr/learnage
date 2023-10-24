#!/usr/bin/python
# add exception handling
# add logging to a file
# add timestamp ?
import os
import sys
import urllib;
import time

def ultimatenotification(msg):
    try:
        msg = urllib.quote(msg);
        a = 'https://www.ultimatenotifier.com/items/User/send/uber.koob/message=' + msg + '/password=fuckfacebook'
        #print a
        os.system("wget -nv -nc --no-check-certificate " + a)
        
        # crude rate-limiter
        time.sleep(1)

    except Exception,e:
        errMsg = "kojoney_ultimatenotification.py : ultimatenotification() exception caught = " + `e` + " msg=" + msg
        print "Exception : " + errMsg
        syslog.syslog(errMsg)
                    
if __name__ == "__main__":
    msg = time.ctime() + " -> " + sys.argv[1]
    print "message to send : [" + msg + "]"
    ultimatenotification(msg)
    




