#! /usr/bin/python
import syslog
import os
import googleMail	# my wrapper
import time
import kojoney_ultimatenotification

def processAlert(line) :
    try:
        sender    = "uber.koob@gmail.com"
        password  = "fuckfacebook"
        
        #recipients = "richard.crouch@vodafone.com"
        #recipientList = ["majoralert999@gmail.com","richard.crouch@vodafone.com"]
        recipientList = ["majoralert999@gmail.com"]
        
        line = line.rstrip("\n")
        msg = "Entry read from Alert Queue :  " + line
        print msg
        syslog.syslog(msg)
        
        fields = line.split("|")
        #print fields.__str__()
        
        subject      = fields[1]
        message      = fields[3]
        
        #print "subject : " + subject
        #print "message : " + message
          
        fileList = []
        
        # Send the alert via Googlemail
        print "Sending Kojoney Alert via Googlemail..."
        googleMail.sendViaGmail(sender,password,recipientList,subject,message,fileList)
        msg = "kojoney_alert_server.py : processAlert() : Sent Kojoney Alert via Googlemail"
        print msg
        syslog.syslog(msg)  
        
        time.sleep(2)	# crude rate limiter
        
        # Send via Ultimate Notification direct to iPhone
        unMsg = subject + " : " + message
        print "kojoney_alert_server.py : ultimateNotification msg=" + unMsg
        kojoney_ultimatenotification.ultimatenotification(unMsg)
        
        msg = "kojoney_alert_server.py : processAlert() : Sent Kojoney Alert via Ultimate Notification to iPhone"
        print msg
        syslog.syslog(msg)  
        
        #print "kojoney_alert_server.py : processAlert() : done"
        return
         
    except Exception, e:
        msg = "processAlert() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        
        
# --------------------------------------------

def main():
    try:
        syslog.openlog("kojoney_alert_server")
        syslog.syslog("Started")
                
        filenameAlert   = '/tmp/kojoney_alert_queue.txt'  
        fileAlert       = open(filenameAlert,'r')
        st_resultsAlert = os.stat(filenameAlert)
        st_sizeAlert    = st_resultsAlert[6]
        fileAlert.seek(st_sizeAlert)
          
        #print "system     : Seek to end of " + filenameAlert
  
        while True:
            whereAlert = fileAlert.tell()
            lineAlert  = fileAlert.readline()
            if not lineAlert:               # no data in feed  
                #print "Nothing in Kojoney Alert Queue to process"
                fileAlert.seek(whereAlert)
            else :                  #       new data has been added to log file
                #print "*** NEW EVENT in Kojoney Alert Queue to process !"
                processAlert(lineAlert)                                                                                            
            time.sleep(5)         
                                                                                                                   
    except Exception,e:
        msg = "main() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)    
    
  
if __name__ == '__main__' : 
    main()
                                              