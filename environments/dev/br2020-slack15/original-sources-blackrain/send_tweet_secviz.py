#!/usr/bin/python
#
import time, os , syslog  
import send_mail		# RCH library

# The files are actually .csv format, but if named .xls, this allows
# Blackberry to at least view them although they are not imported into columns etc.
# Need to find a way of outputting actual .xls format
# Blackberry will not view files with .csv extension
       
# ----------------------------------------------
        
syslog.syslog("send_tweet_secviz.py run")

# list of files to be e-mailed
files = ['/var/ossec/logs/alerts/alerts.log']

# list of files to be e-mailed
#files = ['/home/var/secviz/router.gif',\
#'/home/var/secviz/honeypot.gif',\
#'/home/var/log/user_activity.csv',\
#'/home/var/log/ids_lastn.rtf',\
#'/home/var/log/ips_lastn.rtf',\
#'/home/var/log/ids_ips_lastn.rtf',\
#'/home/var/log/web_activity.csv',\
#'/home/var/log/secviz.csv',\
#'/home/var/log/secviz_router.csv',\
#'/home/var/log/snort.report.rtf',\
#'/home/var/log/tweets_log_lastn.csv',\
#'/home/var/log/kojoney_tail_secviz5_tweets_lastn.csv',\
#'/home/var/log/kojoney_tail_lastn.csv',\
#'/home/var/secviz/honeypot.dot',\
#'/home/var/secviz/router.dot',\
#'/home/var/log/psad/psad_status.rtf',\
#'/home/snort/rules/local.rules']

powerusers =['ipbb.mvtc@googlemail.com']
text = \
"""This e-mail is generated automatically by the Gloworm Honeypot Monitoring System.

"""
#The .dot file is for import into the Tulip visualisation software.
#The snort.report.txt file is produced by snort_stat.pl software.
#The honeypot.gif/.dot contains honeypot and router events.
#The router.gif/.dot   contains router-only events.
#
#"""

send_mail.send_mail('the.crouches@btconnect.com',powerusers,"*** Honeypot *** : Daily Power User Report(s)" , text, files, 'smtp.btconnect.com')

###################################################
# Send the more interesting files to normal users #
###################################################

files = ['/home/var/secviz/honeypot.gif']
#files = ['/home/var/secviz/darknet.gif','/home/var/log/darknet.log.viz.lastn']

#users = ['richard.crouch@vodafone.com','softlad@vodafone.net']
users = ['richard.crouch@vodafone.com']

text = \
"""This e-mail is generated automatically by the Gloworm Honeypot Monitoring System.

.gif files have been generated using the Afterglow application.

Target node colour key :
PSAD - Active Response : Snort IDS events are detected and cause the offending source IP to be blocked for 10 minutes.
p0f - Passive OS Fingerprinting shows probable OS family based on incoming TCP SYN packet contents.

Events colour key :
White -> RECONAISSANCE phase for commonly-used TCP/UDP ports
Yellow -> RECONNAISSANCE phase for less commonly-used TCP/UDP ports
Orange -> EXPLOIT phase events, i.e. detected by Snort IDS or dropped/filtered by FWSnort IPS
Pink -> Netflow events that look suspicious e.g. NetBIOS or SSH sessions that have duration > 20 seconds etc.
Magenta -> REINFORCEMENT phase , i.e. haxx0r/malware is retrieving software/second stage from another source.

Malware emulation uses the following applications :-
1. AMUN 
2. Nepenthes
3. Dionaea
4. Honeyd

You can receive notification of key events from the honeypot using Twitter by following @honeytweeter
Please note that you will probably need a Twitter client capable of handling multiple accounts since this feed has a high update rate.


If you wish to be removed from this e-mail list or require additional reports, please contact richard.crouch@vodafone.com

"""

# Experimental Dark IP monitoring for VF Ghana
#text = \
#"""This e-mail is generated automatically by the NSU Gloworm Darknet monitoring system.
#
#darknet.gif     : This event graph shows traffic with destination IP addresses in RFC1918 or Dark IP space.
#darknet.log.viz : This is the raw data used to construct the event graph. 
#
#Only source IPs that have a fan-out of at least 2 are added to the graph.
#
#If you wish to be removed from this e-mail list or require additional reports, please contact richard.crouch@vodafone.com
#
#"""

#send_mail.send_mail('the.crouches@btconnect.com',users,"*** Honeypot *** : Daily User Report(s)" , text, files, 'smtp.btconnect.com')
