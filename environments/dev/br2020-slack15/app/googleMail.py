import os, re
import sys
import smtplib
import time
import syslog
 
from email.mime.multipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders 

#directory = "/tmp/images/"

# This can also be used to NOT send attachments if files=[]
def sendViaGmail(sender,password,recipient,subject,message,files):

    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT   = 587
    recipientList = []
    
    if type(recipient) == 'str':
        recipientList.append(recipient)
    else:
        recipientList = recipient
        
    #print "recipientList : " + recipientList.__str__()
    for person in recipientList:    
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['To']      = person
        msg['From']    = sender

        #print "sendViaGmail()"
        #print " sender      : " + sender
        #print " recipient   : " + recipient
        #print " subject     : " + subject
        #print " message     : " + message
        #print " attachments : " + files.__str__()
    
        msg.attach(MIMEText(message))   # the text in the message

        for filepath in files:

            filename = filepath.split("\\")[-1]
            #print "filepath : " + filepath
            #print "filename : " + filename        

            part = MIMEBase('application',"octet-stream")
            part.set_payload(open(filepath, 'rb').read())
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % filename)
            #part.add_header('Content-type', "text/csv")
            msg.attach(part)
 

        session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
 
        session.ehlo()
        session.starttls()
        session.ehlo
        session.login(sender, password)
  
        session.sendmail(sender, recipient, msg.as_string())
        session.quit()
        
        msg = "sendViaGmail() sent email => To:" + person + " Subject:" + subject
        syslog.syslog(msg)
        print msg
        
        time.sleep(5)
 
if __name__ == '__main__':
        
    sender    = 'uber.koob@gmail.com'
    password  = "fuckfacebook"
    #recipient = 'richard.crouch@vodafone.com'
    recipient = ['richard.crouch100@gmail.com']

    # TEST #1 - no attachment
    subject   = 'googlemail.py : test with no attachments'
    message   = 'No attachments - just an email alert - sent at ' + time.ctime()
    
    fileList = []

    print "Sending test email with NO attachment..."
    sendViaGmail(sender,password,recipient,subject,message,fileList)

    #sys.exit(0)
    
    # TEST #2 - with attachment
    subject   = 'googleMail.py : test with attachments'
    message   = 'Reports attached - sent at ' + time.ctime()
    
    #fileList = ['c:\\temp\\tier1.csv']
    #fileList = ['c:\\temp\\tiny.csv-NMAP.csv','c:\\temp\\tiny.csv-BGPG.csv','c:\\temp\\tiny.csv-DNS.csv']
    fileList = ['googleMail.py']
    
    print "Sending test email WITH attachments..."
    sendViaGmail(sender,password,recipient,subject,message,fileList)

    print "Finished."
