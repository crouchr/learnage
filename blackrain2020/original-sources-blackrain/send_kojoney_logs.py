#!/usr/bin/python
# todo : add date to e-mail 

import time, os , syslog  
import send_mail		# RCH library
       
# ----------------------------------------------
        
syslog.syslog("send_kojoney_logs.py run")
                 
files = ['/home/var/log/tweets.log.txt']

recipients =['richard.crouch@vodafone.com']

text = "This e-mail is generated automatically by the Gloworm Honeypot Monitoring system\nTo be removed, contact richard.crouch@vodafone.com"

#print files

send_mail.send_mail('the.crouches@btconnect.com',recipients,"*** Honeypot *** : Daily Tweet Report" , text, files , 'smtp.btconnect.com')




                              