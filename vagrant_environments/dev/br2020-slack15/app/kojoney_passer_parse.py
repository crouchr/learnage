#!/usr/bin/python

import time,sys,os , syslog , re 
import kojoney_hiddenip
#import kojoney_funcs
#import kojoney_afterglow
import ipintellib

#*** Tweet : PASSER,TS 64.206.169.73 TCP_80 http://p/Apache httpd/ v/2.2.11/ i/(Win32) mod_ssl/2.2.11 OpenSSL/0.9.8i PHP/5.2.9/
#*** Tweet : PASSER,TS 64.206.169.73 TCP_88 http://p/Microsoft IIS httpd/ v/6.0/ o/Windows/
#*** Tweet : PASSER,TS 64.206.169.73 TCP_135 msrpc://p/Microsoft Windows RPC/ o/Windows/
#*** Tweet : PASSER,TS 64.206.169.73 TCP_443 ssl://p/OpenSSL/ i/SSLv3/
#*** Tweet : PASSER,TS 64.206.169.73 TCP_445 microsoft-ds://p/Microsoft Windows 2003 or 2008 microsoft-ds/ o/Windows/
#*** Tweet : PASSER,TS 64.206.169.73 TCP_1025 msrpc://p/Microsoft Windows RPC/ o/Windows/
#*** Tweet : PASSER,TS 64.206.169.73 TCP_3306 mysql://p/MySQL/ i/unauthorized/
#*** Tweet : PASSER,TS 64.206.169.73 TCP_5800 vnc-http://p/RealVNC/ v/4.0/ i/Resolution 400x250; VNC TCP port: 5900/
#*** Tweet : PASSER,TS 64.206.169.73 TCP_5900 vnc://p/VNC/ i/protocol 3.8/
#*** Tweet : PASSER,TS 176.65.164.111 TCP_21 ftp://p/ProFTPD/ o/Unix/
#*** Tweet : PASSER,TS 176.65.164.111 TCP_22 ssh://p/OpenSSH/ v/5.5/ i/protocol 2.0/
#*** Tweet : PASSER,TS 176.65.164.111 TCP_25 smtp://p/Exim smtpd/ h/78-159-102-169.inferno.name/ v/4.63/
#*** Tweet : PASSER,TS 176.65.164.111 TCP_53 domain://p/ISC BIND/ i/Fake version: 9.7.3-RedHat-9.7.3-1.el5/
#*** Tweet : PASSER,TS 176.65.164.111 TCP_80 http://p/Apache httpd/ v/2.2.18/ i/(CentOS)/
#*** Tweet : PASSER,TS 176.65.164.111 TCP_110 pop3://p/Dovecot pop3d/
#*** Tweet : PASSER,TS 176.65.164.111 TCP_143 imap://p/Dovecot imapd/
#*** Tweet : PASSER,TS 176.65.164.111 TCP_443 ssl://p/OpenSSL/ i/SSLv3/
#*** Tweet : PASSER,TS 176.65.164.111 TCP_993 ssl://p/OpenSSL/ i/SSLv3/
#*** Tweet : PASSER,TS 176.65.164.111 TCP_8000 dominoconsole://p/Lotus Domino Console/ o/ Bad HTTP/0.9 request type ('\x80\x82\x01\x03\x01\x00i\x00\x00\x00\x10\x00
#\x00\x05\x00\x00\x04\x01\x00\x80\x00\x00\x02\x00\x00\x08\x00\x00\x14\x00\x00\x03\x02\x00\x80\x00\x00\x01\x00\x00\x15\x00\x00\x06\x04\x00\x80\x00\x00\x16\x00\x00\x
#17\x00\x003\x00\x009\x00\x00\x19\x00\x00/ h/title>
#*** Tweet : PASSER,TS 176.65.164.111 TCP_3306 mysql://p/MySQL/ i/Host blocked because of too many connections/
#*** Tweet : PASSER,TS 46.165.193.12 TCP_22 ssh://p/OpenSSH/ v/4.3/ i/protocol 2.0/
#*** Tweet : PASSER,TS 108.62.85.190 TCP_8080 http-proxy://p/Squid webproxy/ v/3.1.6/
#*** Tweet : PASSER,TS 78.46.145.33 TCP_22 ssh://p/OpenSSH/ v/5.3/ i/protocol 2.0/
#*** Tweet : PASSER,TS 78.46.145.33 TCP_80 http-proxy://p/Squid webproxy/ v/3.1.10/
#*** Tweet : PASSER,TS 78.46.145.33 TCP_3128 http-proxy://p/Squid webproxy/ v/3.1.10/
#*** Tweet : PASSER,TS 78.46.145.33 TCP_8080 http://p/Apache httpd/ v/2.2.15/ i/(CentOS)/
#*** Tweet : PASSER,TS 60.166.28.38 TCP_80 http://p/Apache httpd/ v/2.0.63/ i/(Win32) PHP/5.2.12/
#*** Tweet : PASSER,TS 60.166.28.38 TCP_1025 msrpc://p/Microsoft Windows RPC/ o/Windows/
#*** Tweet : PASSER,TS 60.166.28.38 TCP_3306 mysql://p/MySQL/ i/unauthorized/


def passerViz(line):
    try:
        print "---"    
        version = "?"
        os = "?"
                
        #print "Entered passerViz() : " + line
        line = line.rstrip("\n")
        fields = line.split(",")
        print fields
        
        ip   = fields[1]
        port = fields[2]
        info = fields[4]

        geoIP = ipintellib.geo_ip(ip)
        cc = geoIP['countryCode']
        print cc
        
        print "info(raw)   = " + info
        infoRaw = info
        
        info = info.replace("/",":")
        
        print "ip     = " + ip
        print "port   = " + port
        info = info.replace("protocol ","protocol_")
        info = info.replace(":::",":")
        info = info.replace(" beta","beta")
        
        info = info.replace("Microsoft IIS SSL","MS_IIS_SSL")
        info = info.replace("Microsoft IIS","MS_IIS")
        info = info.replace("Microsoft Windows RPC","MS_RPC")
        info = info.replace("Microsoft Windows daytime","MS_TIME")
        info = info.replace("Microsoft SQL Server","MS_SQL")
        info = info.replace("Microsoft Terminal Service","MS_TS")
        info = info.replace("Microsoft DNS","MS_DNS")
        info = info.replace("Microsoft ftpd","MS_FTPD")
        
        info = info.replace("Apache Jserv","JSERV")
        info = info.replace("Internet Rex","REX")
        info = info.replace("Courier pop3d","COURIER_POP3D")
        info = info.replace("Postfix smtpd","POSTFIX_SMTPD")
        info = info.replace("Linux telnetd","LINUX_TELNETD")
        info = info.replace("Linux SNMP multiplexer","LINUX_SMUX")
        info = info.replace("Cisco SSH","CISCO_SSH")
        info = info.replace("Cisco IOS http","CISCO_HTTPD")
        info = info.replace("Cisco SIP Gateway","CISCO_SIP")
        info = info.replace("Oracle HTTP Server","ORACLE_HTTPD")
        info = info.replace("Oracle XML DB Enterprise","ORACLE_XML_DB")
        info = info.replace("ISC BIND","BIND")
        info = info.replace("SCS sshd","SCS_SSHD")
        info = info.replace("osiris host IDS agent","OSIRIS_AGENT")
        
        print "info(post)  = " + info
        
        infofields = info.split(" ")
        print "infofields = " + infofields.__str__()
        
        for i in infofields :
            #print "i = " + i.__str__()
            if i.find(":p:") >= 0 :
                program = i.rstrip(":")
                program = i.lstrip(":")
                
                # 
                program = program.replace("http:p:","")
                program = program.replace("ssl:p:","")
                program = program.replace("mysql:p:","")
                program = program.replace("msrpc:p:","")
                program = program.replace("http-proxy:p:","")
                program = program.replace("proxy:p:","")
                program = program.replace("openSSH:p:","")
                program = program.replace("imap:p:","")
                program = program.replace("ajp13:p:","JSERV")
                program = program.replace("ms-sql-s:p:","SQL")
                program = program.replace("pop3:p:","POP3")
                program = program.replace("telnet:p:","TELNETD")
                program = program.replace("ident:p:","")
                program = program.replace("smtp:p:","")
                program = program.replace("ftp:p:","")
                program = program.replace("dominoconsole:p:","-")
                #program = program.replace("domain:p:","DNS")
                program = program.replace("microsoft-ds:p:","")
                #program = program.replace("ssh:p:","SSH")
                program = program.replace("nagios-nsca:p:","")                
                print "program found in " + i.__str__() + " is " + program.__str__()
        
            if i.find("v:") >= 0 :
                version = i.rstrip(":")
                version = version.lstrip(":")
                version = version.replace("v:","")
                print "version  found in " + i.__str__() + " is " + version.__str__()
        
            if i.find("i:") >= 0 :
                info = i.rstrip(":")
                info = info.lstrip(":")
                info = info.replace("protocol_","")
                print "info     found in " + i.__str__() + " is " + info.__str__()

            if i.find("o:") >= 0 :
                os = i.rstrip(":")
                os = os.lstrip(":")
                os = os.replace("Windows","W")
                os = os.replace("Linux","L")
                os = os.replace("Unix","U")
                os = os.replace("IOS","I")
                os = os.replace("o:","")
                os = os.rstrip("\n")
                print "os       found in " + i.__str__() + " is " + os.__str__()

        now = time.time()
        nowLocal = time.gmtime(now)
        tstamp = time.asctime(nowLocal)

        msg = "passerViz() : ip=" + ip.__str__() + " port=" + port.__str__() + " program=" + program.__str__() + " os=" + os.__str__()
        syslog.syslog(msg)
        
        fp = open("/home/var/secviz/passer.csv","a")
                    
        msg1 = port + "," + program + "," + tstamp + "," + infoRaw
        print msg1
        print >> fp, msg1
        
        msg2 = program + version + "," + program + "," + tstamp + "," + infoRaw
        print msg2 
        print >> fp, msg2
        
        msg3 = ip + ":" + cc + ":" + os + "," + program + version + "," + tstamp + "," + infoRaw
        print msg3
        print >> fp, msg3
        
        fp.close()
          
    except Exception,e:
        msg = "kojoney_passer_parse.py : passerViz() : " + `e` + " line=" + line
        syslog.syslog(msg)
        return None



# input file
#asset,port,proto,service,application,discovered
#192.168.1.62,0,0,ARP,0:0C:29:A1:DD:89,1319179688
#192.168.1.64,0,0,ARP,0:0C:29:A1:DD:89,1319180259
#192.168.1.64,22,6,ssh,OpenSSH 5.1 (Protocol 2.0),1319180259
#192.168.1.63,0,0,ARP (Intel Corporation),0:04:23:3C:E3:F8,1319181827
#192.168.1.64,2222,6,ssh,OpenSSH 5.1p1 (Protocol 2.0),1319182621
#192.168.1.62,18080,6,www,Apache 2.2.6 (Unix),1319184113
#192.168.1.66,0,0,ARP,0:0C:29:A1:DD:89,1319193351
# return the Tweet or None

def processPasser(line):
    
    try :
        #print "processPasser() : line read is " + line

        # Only interested in TC and UC events
        if line.find("TS") == -1 and line.find("UC") == -1 :
            return None
            
        # Not interested in local listeners    
        fields = line.split(",")
        #print fields
        
        # make sure that the IP is not part of network services e.g. Twitter, Slackware etc.        
        print "*** kojoney_passer_parse.py : calling hiddenIP() ***" 
        if kojoney_hiddenip.hiddenIP(fields[1],False) == True :
            return None
        
        #a = len(fields)
        
        #if a >= 5 and len(fields[4]) > 0 and line.find('/p/') != -1 :
        if line.find('/p/') != -1 or line.find(' i/') != -1 or line.find(' /d') != -1 or line.find(' o/') != -1 or line.find(' v/') != -1 or line.find(' h/') != -1 : 
            msg = line.replace("," ," ")
            msg = msg.replace("listening ", "")            
            msg = "PASSER," + msg
            passerViz(line)
            return msg
        else:
            return None

    except Exception,e:
        syslog.syslog("kojoney_passer_parse.py : processPasser() : " + `e` + " line=" + line)
        return None
                               
# -------------------------------------------------------
        
# Start of code
# This is a test harness so comment/uncomment the relevent lines        
        
if __name__ == '__main__' :
       
# Set the input file to scan
    #filename = '/home/var/log/passer.csv.test'
    filename = '/home/var/log/passer.csv'
    file = open(filename,'r')

    while True:
    
        # Tweets log file       
        # where = file.tell()
        line  = file.readline()
        line  = line.rstrip('\n')
        
        if not line:		# no data to process
            sys.exit()
        else :			# new data has been found
            msg = processPasser(line)
            
        if msg != None:
            print "*** Tweet : " + msg
                       
        #print "sleeping..."
        # this can be a float for sub-second sleep    
        time.sleep(0.01)		# 0.1 
                              
                 