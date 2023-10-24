#!/usr/bin/python
#
import time, os , syslog , sys  
#import send_mail		# RCH library
import checkFilesExist		# RCH library
import googleMail		# RCH library

# The files are actually .csv format, but if named .xls, this allows
# Blackberry to at least view them although they are not imported into columns etc.
# Need to find a way of outputting actual .xls format
# Blackberry will not view files with .csv extension
       
# ----------------------------------------------

print "Synchronise clocks..."
os.system("ntpdate uk.pool.ntp.org")

syslog.openlog("send_drone_reports")         # Set syslog program name          

syslog.syslog("send_drone_reports.py started")

# list of files to be e-mailed
#files = ['/home/var/secviz/drone.gif','/home/var/log/kojoney_fprint.csv','\
#/home/var/secviz/drone.dot','/home/var/log/dronetracer.pcap',\
#'/home/var/secviz/honeysnap.txt','/home/var/log/sebek.log.txt','/home/var/log/kojoney_sebek.csv']
#,\
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


# THIS IS THE CORRECT CODE HERE
#files = [\
#'/home/var/log/blackrain_amun.pcap',\
#'/home/var/log/blackrain_kippo.pcap',\
#'/home/var/log/blackrain_honeyrtr.pcap',\
#'/home/var/log/blackrain_honeytrap.pcap',\
#'/home/var/log/blackrain_nepenthes.pcap',\
#'/home/var/log/blackrain_glastopf.pcap',\
#'/home/var/log/blackrain_telnetd.pcap',\
#'/home/var/log/blackrain_spam.pcap',\
#'/home/var/log/pads-assets.csv',\
#'/home/var/log/passer.csv',\
#'/home/var/log/honeytrap.log',\
#'/home/var/log/snort.report.rtf',\
#'/home/var/log/tweetsofinterest.txt',\
#'/home/var/secviz/webscan.gif',\
#'/home/var/secviz/webscan.dot',\
#'/home/var/secviz/honeyd.gif',\
#'/home/var/secviz/honeyd.dot',\
#'/home/var/secviz/amun_x.gif',\
#'/home/var/secviz/amun_x.dot',\
#'/home/var/secviz/aspath.gif',\
#'/home/var/secviz/aspath.csv',\
#'/home/var/secviz/aspath.dot',\
#'/home/var/secviz/failedCredentialsViz.csv',\
#'/home/var/secviz/failedcredentials.gif',\
#'/home/var/secviz/failedcredentials.dot',\
#'/home/var/secviz/passer.csv',\
#'/home/var/secviz/passer.gif',\
#'/home/var/secviz/passer.dot',\
#'/home/var/secviz/nmap.gif',\
#'/home/var/secviz/nmap.csv',\
#'/home/var/secviz/nmap.dot'
#'/usr/local/src/amun/logs/shellcode_manager.log' 
#]

files = [\
'/home/var/log/datacapture_pcap/blackrain_amun.pcap',\
'/home/var/log/datacapture_pcap/blackrain_honeytrap.pcap',\
'/home/var/log/datacapture_pcap/blackrain_glastopf.pcap',\
'/home/var/log/datacapture_pcap/blackrain_telnetd.pcap',\
'/home/var/log/datacapture_pcap/blackrain_snmpd.pcap',\
'/home/var/log/datacapture_pcap/blackrain_spam.pcap',\
'/home/var/log/datacapture_pcap/blackrain_conpot.pcap',\
'/usr/local/src/snortalog/blackrain-snortalog.html',\
'/usr/local/src/snortalog/blackrain-attacker-snortalog.html'
]

#home/var/log/blackrain_snort.rtf']

# build a list of all files that are larger than 256 bytes
filesExist = checkFilesExist.gatherNonZeroFiles(files,256)
print filesExist

powerusers =['honeytweeter@gmail.com']
#ipbb.mvtc@googlemail.com

#powerusers =['ipbb.mvtc@googlemail.com','aamsa14@gmail.com']
# syed = aamsa14@gmail.com
#powerusers =['richard.crouch@vodafone.com','ipbb.mvtc@googlemail.com']

#text = \
#"""This e-mail is generated automatically by the BlackRain honeypot.
#
#mware_collect_nepenthes.pcap : pcap file for all traffic to from Nepenthes malware collector.
#blackrain_linux_honeypot.pcap  : pcap file for all traffic to/from Slackware 11.0 Linux honeypot.
#
#"""

#text = \
#"""This e-mail is generated automatically by the BlackRain honeynet system.
#
#Packet Capture(s)
#-----------------
#blackrain_amun.pcap        : pcap file for all traffic to/from Amun Win32 malware collector.
#blackrain_kippo.pcap       : pcap file for all traffic to/from Kippo SSHd Linux honeypot.
#blackrain_honeyrtr.pcap    : pcap file for all traffic to/from honeypotted router (Telnet/SNMP).
#blackrain_honeytrap.pcap   : pcap file for all traffic to/from Honeytrap low-interaction honeypot.
#blackrain_nepenthes.pcap   : pcap file for all traffic to/from Nepenthes Win32 malware collector.
#blackrain_glastopf.pcap    : pcap file for all traffic to/from Glastopf Web honeypot.
#blackrain_telnetd.pcap     : pcap file for all traffic to/from Telnetd honeypot.
#
#Log File(s)
#-----------
#kippo_failed_attempts.log  : Username/passwords used agains Kippo SSHd Linux honeypot.
#pads-assets.csv            : Honeynet assets discovered each day by PADS
#passer.csv                 : Passer : Passive Discovery tool log file
#tweetsofinterest.txt       : Daily list of Tweets matching keywords
#failedCredentialsViz.csv   : Daily list SSH/Telnet login credentials
#
#AfterGlow Visualisation(s)
#--------------------------
#webscan.gif                : HTTP scans against Glastopf Web honeypot.
#honeyd.gif                 : IP network scans against Honeyd honeypot.
#aspath.gif                 : Traceroutes (including AS info) to attacker IPs.
#nmap.gif                   : Open ports on attacker IPs according to Nmap.
#passer.gif                 : Open applications on attacker IPs according to Passer.
#failedcredentials.gif      : SSH/Telnet account attempts.
#
#Other
#-----
#snort.report.rtf           : Snort NIDS alerts report.
#
#
#To be removed from this distribution list, e-mail the BlackRain admin : honeytweeter@gmail.com
#
#"""

text = \
"""This e-mail is generated automatically by the BlackRain honeynet system.

Packet Capture(s)
-----------------
blackrain_amun.pcap        : pcap file for all traffic to/from Amun Win32 malware collector.
blackrain_honeytrap.pcap   : pcap file for all traffic to/from Honeytrap low-interaction honeypot.
blackrain_glastopf.pcap    : pcap file for all traffic to/from Glastopf Web honeypot.
blackrain_telnetd.pcap     : pcap file for all traffic to/from Telnetd honeypot.
blackrain_spam.pcap        : pcap file for all traffic to/from SMTP honeypot.
blackrain_snmp.pcap        : pcap file for all traffic to/from SNMP honeypot.

Other
-----
blackrain_snort.rtf        : Snort NIDS alerts report.


To be removed from this distribution list, e-mail the BlackRain admin : honeytweeter@gmail.com

"""

#send_mail.send_mail('the.crouches@btconnect.com',powerusers,"*** DroneTracer *** : Daily Power User Report(s)" , text, files, 'smtp.btconnect.com')
print "Sending e-mail to " + `powerusers` + " ..."

# This e-mail needs to come from a gmail account since I am tied to BT line otherwise 
#send_mail.send_mail('richard_crouch@btconnect.com' , powerusers , "BlackRain : Data Capture Report" , text , filesExist , 'smtp.btconnect.com')
googleMail.sendViaGmail('uber.koob@gmail.com' , 'fuckfacebook' , powerusers , "BlackRain : Data Capture Report" , text , filesExist)

###################################################
# Send the more interesting files to normal users #
###################################################

#files = ['/home/var/secviz/honeypot.gif']
#files = ['/home/var/secviz/darknet.gif','/home/var/log/darknet.log.viz.lastn']

#users = ['richard.crouch@vodafone.com','softlad@vodafone.net']
#users = ['richard.crouch@vodafone.com']

#text = \
#"""This e-mail is generated automatically by the Gloworm Honeypot Monitoring System.
#
#.gif files have been generated using the Afterglow application.
#
#Target node colour key :
#PSAD - Active Response : Snort IDS events are detected and cause the offending source IP to be blocked for 10 minutes.
#p0f - Passive OS Fingerprinting shows probable OS family based on incoming TCP SYN packet contents.
#
#Events colour key :
#White -> RECONAISSANCE phase for commonly-used TCP/UDP ports
#Yellow -> RECONNAISSANCE phase for less commonly-used TCP/UDP ports
#Orange -> EXPLOIT phase events, i.e. detected by Snort IDS or dropped/filtered by FWSnort IPS
#Pink -> Netflow events that look suspicious e.g. NetBIOS or SSH sessions that have duration > 20 seconds etc.
#Magenta -> REINFORCEMENT phase , i.e. haxx0r/malware is retrieving software/second stage from another source.
#
#Malware emulation uses the following applications :-
#1. AMUN 
#2. Nepenthes
#3. Dionaea
#4. Honeyd
#
#You can receive notification of key events from the honeypot using Twitter by following @honeytweeter
#Please note that you will probably need a Twitter client capable of handling multiple accounts since this feed has a high update rate.
#
#
#If you wish to be removed from this e-mail list or require additional reports, please contact richard.crouch@vodafone.com
#
#"""
#
#
#send_mail.send_mail('the.crouches@btconnect.com',users,"*** Honeypot *** : Daily User Report(s)" , text, files, 'smtp.btconnect.com')

syslog.syslog("send_drone_reports.py finished")

print "done."

