#!/usr/bin/python
# todo : encrypt the source code so only I have it
# add :
# other major source code - p0f, python libraries
# cron.daily shell file
# ntp conf
#
import time, os , syslog  
import send_mail		# RCH library
import checkFilesExist		# RCH library       
# ----------------------------------------------
        
syslog.openlog("send_blackrain_sources")         # Set syslog program name    

syslog.syslog("send_blackrain_sources.py : Started")

# list of files to be e-mailed
files = ['/home/crouchr/blackrain_dev/blackrainclient.py',\
'/home/crouchr/blackrain_dev/blackrain_bootstrap.py',\
'/home/crouchr/blackrain_dev/blackrain_ipintellib.py',\
'/home/crouchr/send_blackrain_sources.py',\
'/home/crouchr/blackrain_dev/blackrain_ipintellib.test.in.csv',\
'/home/crouchr/blackrain_dev/blackrain_super.py',\
'/home/crouchr/blackrain_dev/register.py',\
'/home/crouchr/blackrain_dev/blackrain.log',\
'/home/crouchr/blackrain_dev/blackrain_stun.py',\
'/home/crouchr/blackrain_dev/blackrain_default_gw.py',\
'/home/crouchr/blackrain_dev/blackrain_cpuinfo.py',\
#'/home/crouchr/blackrain_dev/setuptools-0.6c11.tar.gz',\
#'/home/crouchr/blackrain_dev/IPy-0.62.tar']
#'/home/crouchr/blackrain_dev/netifaces-0.5.tar.gz',\
'/home/crouchr/blackrain_dev/blackrain_mac.py']

# Generate a list of the files that exist
a = len(files)

filesExist=checkFilesExist.gatherNonZeroFiles(files,1)
b = len(filesExist)
print filesExist

if a != b:
    msg = "Some expected source files could not be found : expected=" + `a` + " actual=" + `b`
    print "\nWARNING : " + msg
    syslog.syslog("send_blackrain_sources.py : " + msg)
    
#recipients =['ipbb.mvtc@googlemail.com']
#recipients =['richard.crouch@vodafone.com']
recipients =['uber.koob@gmail.com']

text = "This e-mail is generated automatically by 'mars'\n"

print "recipients = " + recipients.__str__()
send_mail.send_mail('richard_crouch@btconnect.com',recipients,"BlackRain Sensor : Source code" , text, filesExist, 'smtp.btconnect.com')

syslog.syslog("send_blackrain_sources.py : Finished, " + `b` + " BlackRain Sensor source files backed up to " + `recipients`)

