#! /usr/bin/python

# Master is on mars

#import sys
#import os
#import re

#from ssmtplib import SMTP_SSL as SMTP       # this invokes the secure SMTP protocol (port 465, uses SSL)
from smtplib import SMTP                  # use this for standard SMTP protocol   (port 25, no encryption)
from email.MIMEText import MIMEText

def mailalert(sender,destination,smtpServer,subject,content,debugLevel):
    
    # Only needed for S/SMTP
    #USERNAME = "the.crouches@btconnect.com"
    #PASSWORD = "PASSWORD_INTERNET_SERVICE_PROVIDER"

    # typical values for text_subtype are plain, html, xml
    text_subtype = 'plain'

    try:
        msg = MIMEText(content, text_subtype)
        msg['Subject']=       subject
        
        #print "Connect to SMTP server..."
        conn = SMTP(smtpServer)
        conn.set_debuglevel(debugLevel)
        #conn.login(USERNAME, PASSWORD)
        try:
            #print "Sending e-mail..."
            conn.sendmail(sender, destination, msg.as_string())
        finally:
            #print "Closing SMTP connection..."
            conn.close()
            return True
                                                
    except Exception, exc:
        #print "Failed to send email"
        #sys.exit( "mail failed; %s" % str(exc) )
        return False
        
# --------------------------------------------

def main():

    smtpServer  = 'smtp.btconnect.com'
    sender      = 'the.crouches@btconnect.com'
    destination = ['richard.crouch@vodafone.com']
    debugLevel  = False
    subject     = "Testing from mailAlert() #3"
    
    #content="""\
    #Test message using mailAlert() test harness
    #This is the second line
    #This is a third line
    #
    #From 
    #
    #Freddy Knowles
    #"""
    
    content='Test message using mailAlert() test harness\nThis is the second line\nThis is a third line\n\nFrom\nFreddy Knowles'

    status = mailalert(sender,destination,smtpServer,subject,content,debugLevel)

    if status == True:
        print "E-mail sent OK"
    else:
        print "E-mail FAILED"    

if __name__ == '__main__': main()
                                              