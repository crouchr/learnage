#!/usr/bin/python
import sys,syslog


# read line by line
while True :
    next = sys.stdin.readline()         # read a one-line string
    if not next:                        # or an empty string at EOF
        break
    
    print "Data received from SIEM : " + next
    syslog.syslog("SIEM : " + next)

            