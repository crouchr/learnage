#! /usr/bin/python

# Master is on mars
import time
import syslog

import googleMail	# my wrapper

# what the application sends
# user-supplied data cannot include | character
def sendAlert(subject,msg,emailFlag,appleFlag) :
    try:

        subject = "BlackRain:" + subject
        alertJob = "subject|" + subject + "|msg|" + msg + "|" + time.ctime()
        print "alertJob " + '"' + alertJob + '"' + " added to queue" 
        
        fpOut = open("/tmp/kojoney_alert_queue.txt",'a')
        print >> fpOut,alertJob
        fpOut.close()
         
    except Exception, e:
        msg = "sendAlert() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)

        
# --------------------------------------------
# TEST HARNESS
# --------------------------------------------
def main():

    subject = "Test from kojoney_alert_client"
    msg     = "Botcode found in /usr/local/src/2376w7672.txt at " + time.ctime()	# add time to make message unique
    
    sendAlert(subject,msg,True,True) 
    
if __name__ == '__main__': 
    main()
                                              