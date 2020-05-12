import smtplib
import os
import syslog

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

def send_mail(send_from, send_to, subject, text, files=[], server="localhost"):
    try:
        assert type(send_to)==list
        assert type(files)==list

        msg = MIMEMultipart()
        msg['From'] = send_from
        msg['To'] = COMMASPACE.join(send_to)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject

        msg.attach( MIMEText(text) )

        for f in files:
            part = MIMEBase('application', "octet-stream")
            part.set_payload( open(f,"rb").read() )
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
            msg.attach(part)

        smtp = smtplib.SMTP(server)
        smtp.sendmail(send_from, send_to, msg.as_string())
        smtp.close()
        return True
        
    except Exception,e:
        msg = "send_mail.py : send_mail() : exception : subject = [" + subject + "], To : " + send_to.__str__() + " : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return False
# main
#recipients = ['richard.crouch@vodafone.com']
#text = "Here are the attachments :"
#files = ['send_mail.py']
#

if __name__ == '__main__' :
    text = "Here's a little bit of padding in the email body"
    recipients = ['honeytweeter@gmail.com']
    files = ['send_mail.py']    
    
    send_mail('richard_crouch@btconnect.com',recipients,"Test message using send_mail.py",text,files,'smtp.btconnect.com')

