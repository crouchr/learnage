#!/usr/bin/python

import socket
import time
import syslog

try:
    syslog.openlog("ossec_syslogd")
    
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    host = socket.gethostname()
    port = 5514
    FILENAME = "/home/var/log/ossec.log"

    s.bind((host,port))

    syslog.syslog("Started, listening for ossec syslog messages on UDP port " + port.__str__() + " outputFile=" + FILENAME)

    #fp = open(FILENAME,'a')
    while True:
        data,addr = s.recvfrom(1024)
        log = data.split("ossec: ")[1]
        msg = time.ctime() + " " + log.__str__()
        fp = open(FILENAME,'a')
        print >> fp,msg
        fp.close()
        
except Exception,e:
    msg = "Exception : " + e.__str__()
    print msg
    syslog.syslog(msg)
    