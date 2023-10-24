#!/usr/bin/python

import time

# line=WEB_SCN,Scan from 218.93.11.18 req=//phpMyAdmin/
# ['WEB_SCN,Scan', 'from', '218.93.11.18', 'req=//phpMyAdmin/']
# *** Tweet : WEB_SCN,Scan from 218.93.11.18 req=//phpMyAdmin/
# 
# line=WEB_PRX,Proxy request from 58.218.204.110 req=http://173.201.161.57/
# ['WEB_PRX,Proxy', 'request', 'from', '58.218.204.110', 'req=http://173.201.161.57/']
# *** Tweet : WEB_PRX,Proxy request from 58.218.204.110 req=http://173.201.161.57/


def visWebScan(line):
    print "visWebScan(): line=" + line
    fields = line.split(" ")
    print fields
    
    # catch very basic problems with truncated messages
    if len(fields) != 5 :
        return
    
    if fields[0] == "WEB_SCN,Scan" or fields[0] == "WEB_PRX,Proxy" :
        msg = fields[3] + "," + fields[4]
        msg = msg.replace("req=","")
        msg = msg.replace("http://","")

        now = time.localtime(time.time())
            
        msg = msg + "," + time.asctime(now)
                                         
            
        filename = "/home/var/log/visualisation/webscan.csv"
        fp       = open(filename,'a')
        print >> fp,msg
        print msg
        fp.close()
        
#['HONEYD_FLOW,tcp', '221.1.220.163', '3644', '[HONEYD]', 'dport=7212', 'rxBytes=199', 'os=Windows']        
def visHoneyd(line):
    #print "visHoneyd(): line=" + line
    fields = line.split(" ")
    #print fields
    
    # catch very basic problems with truncated messages
    if len(fields) != 7 :
        return
    
    #if fields[0] == "HONEYD_FLOW,tcp_SCN,Scan" or fields[0] == "WEB_PRX,Proxy" :
    msg = fields[1] + "," + fields[0].split(',')[1] + fields[4].split("=")[1]
    #print msg
    #    msg = msg.replace("req=","")
    #    msg = msg.replace("http://","")
    #
    now = time.localtime(time.time())            
    msg = msg + "," + time.asctime(now)
                                                 
    filename = "/home/var/log/visualisation/honeyd.csv"
    fp       = open(filename,'a')
    print >> fp,msg
    print msg
    fp.close()




#submitted=Tue Mar 15 08:50:51 2011 cmd=GEO_IP tweet=AMUN_X,AMUN:445 MS08067 Vulnerability: bind://AMUN:1130/ Shellcode: ulm
#submitted=Tue Mar 15 09:44:54 2011 cmd=GEO_IP tweet=AMUN_X,AMUN:445 MS08067 Vulnerability: ftp://ccc:1@60.10.179.100:6054/282.gif Shellcode: plainurl
#submitted=Tue Mar 15 10:06:15 2011 cmd=GEO_IP tweet=AMUN_X,AMUN:135 DCOM Vulnerability: tftp://217.24.72.214:69/host.exe Shellcode: leimbach
#submitted=Tue Mar 15 10:15:13 2011 cmd=GEO_IP tweet=AMUN_X,AMUN:445 MS08067 Vulnerability: http://suhi4hr.net:80/7.exe Shellcode: plainurl
#submitted=Tue Mar 15 10:53:22 2011 cmd=GEO_IP tweet=AMUN_X,AMUN:445 MS08067 Vulnerability: cbackf://193.106.175.180:8831/omoaHw== Shellcode: linkbot
#submitted=Tue Mar 15 11:45:10 2011 cmd=GEO_IP tweet=AMUN_X,AMUN:445 MS08067 Vulnerability: http://suhi4hr.net:80/7.exe Shellcode: plainurl
#submitted=Tue Mar 15 12:29:40 2011 cmd=GEO_IP tweet=AMUN_X,AMUN:445 MS08067 Vulnerability: ftp://ccc:1@60.10.179.100:6054/282.gif Shellcode: plainurl
#submitted=Tue Mar 15 15:31:38 2011 cmd=GEO_IP tweet=AMUN_X,AMUN:445 MS08067 Vulnerability: ftp://ccc:1@60.10.179.100:6054/282.gif Shellcode: plainurl
#submitted=Tue Mar 15 17:27:59 2011 cmd=GEO_IP tweet=AMUN_X,AMUN:445 MS08067 Vulnerability: http://b.suhi4hr.net:80/7.exe Shellcode: plainurl
#submitted=Wed Mar 16 06:17:20 2011 cmd=GEO_IP tweet=AMUN_X,AMUN:445 MS08067 Vulnerability: ftp://ccc:1@60.10.179.100:6054/282.gif Shellcode: plainurl
#submitted=Wed Mar 16 06:20:27 2011 cmd=GEO_IP tweet=AMUN_X,AMUN:445 MS08067 Vulnerability: http://178.211.56.90:80/c11.exe Shellcode: plainurl
#submitted=Wed Mar 16 09:49:34 2011 cmd=GEO_IP tweet=AMUN_X,AMUN:445 MS08067 vulnerability cbackf://193.106.175.180:8831/omoaHw== shellcode=linkbot
#submitted=Wed Mar 16 17:58:36 2011 cmd=GEO_IP tweet=AMUN_X,AMUN:135 DCOM vulnerability tftp://217.227.231.83:69/host.exe shellcode=leimbach
#submitted=Wed Mar 16 18:00:53 2011 cmd=GEO_IP tweet=AMUN_X,AMUN:445 MS08067 vulnerability cbackf://119.115.50.95:13106/km4EhA== shellcode=linkbot
#submitted=Wed Mar 16 18:21:20 2011 cmd=GEO_IP tweet=AMUN_X,AMUN:445 MS08067 vulnerability ftp://ccc:1@60.10.179.100:6054/282.gif shellcode=plainurl
#submitted=Thu Mar 17 05:56:26 2011 cmd=GEO_IP tweet=AMUN_X,AMUN:445 MS08067 vulnerability ftp://ccc:1@60.10.179.100:6054/282.gif shellcode=plainurl
#submitted=Thu Mar 17 06:23:48 2011 cmd=GEO_IP tweet=AMUN_X,AMUN:445 MS08067 vulnerability cbackf://193.106.175.180:8831/omoaHw== shellcode=linkbot
#submitted=Thu Mar 17 08:37:49 2011 cmd=GEO_IP tweet=AMUN_X,AMUN:445 MS08067 vulnerability bind://AMUN:1130/ shellcode=ulm
#submitted=Thu Mar 17 08:40:52 2011 cmd=GEO_IP tweet=AMUN_X,AMUN:445 MS08067 vulnerability ftp://ccc:1@60.10.179.100:6054/282.gif shellcode=plainurl
#submitted=Thu Mar 17 09:24:32 2011 cmd=GEO_IP tweet=AMUN_X,AMUN:445 MS08067 vulnerability ftp://ccc:1@60.10.179.100:6054/282.gif shellcode=plainurl
def visAmunX(line):
    #print "visAmunX(): line=" + line
    #print line
    fields = line.split(" ")
    #print fields
    port      = fields[0].split(",")[4]
    vuln      = fields[1]
    url       = fields[3]
    shellcode = fields[4].split("=")[1].rstrip("]")
    
    #print port
    #print vuln
    #print url
    #print shellcode

    vis = vuln + ":" + port + "," + "sc=" + shellcode + "," + url
    print vis
    
    # catch very basic problems with truncated messages
    #if len(fields) != 7 :
    #    return
    
    #if fields[0] == "HONEYD_FLOW,tcp_SCN,Scan" or fields[0] == "WEB_PRX,Proxy" :
    #msg = fields[1] + "," + fields[0].split(',')[1] + fields[4].split("=")[1]
    #print msg
    #    msg = msg.replace("req=","")
    #    msg = msg.replace("http://","")
    #
    #now = time.localtime(time.time())            
    #msg = msg + "," + time.asctime(now)
                                                 
    #filename = "/home/var/log/visualisation/honeyd.csv"
    #fp       = open(filename,'a')
    #print >> fp,msg
    #print msg
    #fp.close()
        

# Top-layer function selector        
#55,[id55,CN,AMUN_X,AMUN:445 (MS08067 Vulnerability: ftp://ccc:1@60.10.179.100:6054/282.gif) (Shellcode: plainurl)] metadata:lat='39.89',long='115.28',cc=CN,city=Hebei
#56,[id56,GURU,CN,ip=60.10.179.100 NoDNS CHINA169-BACKBONE AS4837 APNIC 60.10.0.0/16,cc=CN city=Hebei] metadata:lat=None,long=None
#57,[id57,CN,NIDS_BRO_LC,AMN->60.10.179.100 other 52599 6054 tcp 65 193 SF L @af-b41-89] metadata:lat='39.89',long='115.28',cc=CN,city=Hebei
#58,[id58,GURU,CN,ip=60.10.179.100 NoDNS CHINA169-BACKBONE AS4837 APNIC 60.10.0.0/16,cc=CN city=Hebei] metadata:lat=None,long=None
#59,[id59,AW,RTR_LOG,%SEC-6-IPACCESSLOGP: 199 permit tcp 201.229.45.247(2968) -> RTR(23), 1 pkt] metadata:lat='12.57',long='-70.02',cc=AW,city=Noord
#60,[id60,--,RTR_AUTH,tty66: Login aborted by request -- msg: Carrier dropped] metadata:lat=None,long=None
#61,[id61,GURU,AW,ip=201.229.45.247 201-229-45-247.setardsl.aw SetarNet AS11816 LACNIC 201.229.40.0/21,cc=AW city=Noord] metadata:lat=None,long=None
#62,[id62,CN,HONEYD_FLOW,udp 202.205.89.79 1029 [HONEYD] dport=44619 rxBytes=144] metadata:lat='39.93',long='116.39',cc=CN,city=Beijing
#63,[id63,GURU,CN,ip=202.205.89.79 NoDNS ERX-CERNET-BKB AS4538 APNIC 202.192.0.0/12,cc=CN city=Beijing] metadata:lat=None,long=None
#1,[id1,EG,RTR_LOG,%SEC-6-IPACCESSLOGP: 199 permit tcp 41.234.230.225(2514) -> RTR(23), 4 pkts] metadata:lat='31.20',long='29.92',cc=EG,city=Alexandria
#2,[id2,GURU,EG,ip=41.234.230.225 host-41.234.230.225.tedata.net TE-AS AS8452 AFRINIC 41.234.128.0/17,city=Alexandria cc=EG] metadata:lat=None,long=None
#3,[id3,CN,HONEYD_FLOW,tcp 221.1.220.163 2695 [HONEYD] dport=9090 rxBytes=205 os=Windows] metadata:lat='35.24',long='115.44',cc=CN,city=Heze
#4,[id4,CN,HONEYD_FLOW,tcp 221.1.220.163 3987 [HONEYD] dport=9415 rxBytes=197 os=Windows] metadata:lat='35.24',long='115.44',cc=CN,city=Heze
#5,[id5,GURU,CN,ip=221.1.220.163 NoDNS CHINA169-BACKBONE AS4837 APNIC 221.0.0.0/15,city=Heze cc=CN] metadata:lat=None,long=None
#6,[id6,GURU,CN,ip=221.1.220.163 NoDNS CHINA169-BACKBONE AS4837 APNIC 221.0.0.0/15,city=Heze cc=CN] metadata:lat=None,long=None
#7,[id7,CN,HONEYD_FLOW,tcp 221.1.220.163 1928 [HONEYD] dport=9090 rxBytes=9 os=Windows:::] metadata:lat='35.24',long='115.44',cc=CN,city=Heze
def visTweet(tweet):
    #print tweet
     
    fields = tweet.split(",")
    #print fields
    #cc  = fields[2]
    src = fields[3]
    #print src
    
    #print "visTweet() : " + tweet
    if src.find("AMUN_X") != -1 :
        visAmunX(tweet)










#submitted=Sun Feb 19 06:33:23 2012 cmd=GEO_IP tweet=NIDS_SH,[1:1394:12] Code x86 inc ecx NOOP [CL:Code] P1 T 64.65.223.36:2541->AMUN:445
#submitted=Sun Feb 19 06:33:24 2012 cmd=GEO_IP tweet=NIDS_SH,[1:1390:8] Code x86 inc ebx NOOP [CL:Code] P1 T 64.65.223.36:2541->AMUN:445
#submitted=Sun Feb 19 06:33:28 2012 cmd=GEO_IP tweet=GURU,US,ip=64.65.223.36 host-64-65-223-36.pit.choiceone.net ONECOM-CTC 13407-ARIN 64.65.216.0/21,city=Aliquippa
#submitted=Sun Feb 19 06:33:38 2012 cmd=GEO_IP tweet=HONEYTRAP,9988/tcp : 65024 bytes from 64.65.223.36:3192.
#submitted=Sun Feb 19 06:33:43 2012 cmd=GEO_IP tweet=IPLOG,TCP portscan detected [ports 139,445] from 64.65.223.36 [ports 4660,4684,4774,1128,1337,...]
#submitted=Sun Feb 19 06:35:09 2012 cmd=GEO_IP tweet=NIDS_SH,[1:1390:8] Code x86 inc ebx NOOP [CL:Code] P1 T 64.65.223.36:2541->AMUN:445
#submitted=Sun Feb 19 06:35:10 2012 cmd=GEO_IP tweet=IPLOG,TCP portscan expired for 64.65.223.36 - received a total of 19 packets (532 bytes).
#submitted=Sun Feb 19 06:35:17 2012 cmd=GEO_IP tweet=FW_SNORT,[:382:] "ICMP PING Windows" ICMP 64.65.223.36->AMUN
#submitted=Sun Feb 19 06:35:20 2012 cmd=GEO_IP tweet=FW_SNORT,[:384:] "ICMP PING" ICMP 64.65.223.36->AMUN
#submitted=Sun Feb 19 06:35:39 2012 cmd=GEO_IP tweet=FW_SNORT,[:2001569:] "Behavioral Unusual Port 445 traffic, Potential Scan or Infection" TCP 64.65.223.36->AMUN
#submitted=Sun Feb 19 06:35:44 2012 cmd=GEO_IP tweet=FW_SNORT,[:2001579:] "Behavioral Unusual Port 139 traffic, Potential Scan or Infection" TCP 64.65.223.36->AMUN
#submitted=Sun Feb 19 06:35:47 2012 cmd=GEO_IP tweet=FW_SNORT,[:2001569:] "Behavioral Unusual Port 445 traffic, Potential Scan or Infection" TCP 64.65.223.36->AMUN
#submitted=Sun Feb 19 06:35:48 2012 cmd=GEO_IP tweet=FW_SNORT,[:2001579:] "Behavioral Unusual Port 139 traffic, Potential Scan or Infection" TCP 64.65.223.36->AMUN
#submitted=Sun Feb 19 06:35:49 2012 cmd=GEO_IP tweet=ANALYST,--,TRACEROUTE : HPOT->US:64.65.223.36
#submitted=Sun Feb 19 06:35:50 2012 cmd=GEO_IP tweet=FW_SNORT,[:2001569:] "Behavioral Unusual Port 445 traffic, Potential Scan or Infection" TCP 64.65.223.36->AMUN
#submitted=Sun Feb 19 06:35:51 2012 cmd=GEO_IP tweet=FW_SNORT,[:2001579:] "Behavioral Unusual Port 139 traffic, Potential Scan or Infection" TCP 64.65.223.36->AMUN
#submitted=Sun Feb 19 06:36:27 2012 cmd=GEO_IP tweet=FW_SNORT,[:2001944:] "ET NETBIOS MS04-007 Kill-Bill ASN1 exploit attempt" TCP 64.65.223.36->AMUN
#submitted=Sun Feb 19 06:36:28 2012 cmd=GEO_IP tweet=FW_SNORT,[:2001944:] "ET NETBIOS MS04-007 Kill-Bill ASN1 exploit attempt" TCP 64.65.223.36->AMUN
#submitted=Sun Feb 19 06:36:29 2012 cmd=GEO_IP tweet=FW_SNORT,[:1390:] "GPL Code x86 inc ebx NOOP" TCP 64.65.223.36->AMUN
#submitted=Sun Feb 19 06:36:33 2012 cmd=GEO_IP tweet=FW_SNORT,[:1390:] "GPL Code x86 inc ebx NOOP" TCP 64.65.223.36->AMUN
#submitted=Sun Feb 19 06:43:50 2012 cmd=GEO_IP tweet=FW_SNORT,[:2001972:] "Behavioral Unusually fast Terminal Server Traffic, Potential Scan or Infection" TCP 82.42.180.26->HTRAP
#submitted=Sun Feb 19 06:43:52 2012 cmd=GEO_IP tweet=GURU,GB,ip=82.42.180.26 cpc12-live22-2-0-cust25.know.cable.virginmedia.com NTL 5089-RIPENCC 82.42.0.0/15,city=Liverpool
#submitted=Sun Feb 19 06:43:54 2012 cmd=GEO_IP tweet=HONEYTRAP,3389/tcp : 42 bytes from 82.42.180.26:61536.
#submitted=Sun Feb 19 06:55:26 2012 cmd=GEO_IP tweet=FW_SNORT,[:2001972:] "Behavioral Unusually fast Terminal Server Traffic, Potential Scan or Infection" TCP 81.208.57.47->HTRAP
#submitted=Sun Feb 19 06:55:32 2012 cmd=GEO_IP tweet=HONEYTRAP,3389/tcp : 42 bytes from 81.208.57.47:61319.
#submitted=Sun Feb 19 06:55:33 2012 cmd=GEO_IP tweet=GURU,IT,ip=81.208.57.47 81-208-57-47.ip.fastwebnet.it FASTWEB 12874-RIPENCC 81.208.0.0/18,city=None
#submitted=Sun Feb 19 06:58:10 2012 cmd=GEO_IP tweet=ANALYST,--,TRACEROUTE : HPOT->ISP->SEABONE-NET->FASTWEB->IT:89.97.200.65
#submitted=Sun Feb 19 07:04:54 2012 cmd=GEO_IP tweet=WEB_SCN,Scan from 62.75.224.214 req=|
#submitted=Sun Feb 19 07:04:55 2012 cmd=GEO_IP tweet=FW_SNORT,[:1768:] "WEB-IIS header field buffer overflow attempt" TCP 62.75.224.214->WEB
#submitted=Sun Feb 19 07:04:59 2012 cmd=GEO_IP tweet=GURU,DE,ip=62.75.224.214 prag193.server4you.de PLUSSERVER-AS 8972-RIPENCC 62.75.128.0/17,city=None
#submitted=Sun Feb 19 07:07:45 2012 cmd=GEO_IP tweet=ANALYST,--,TRACEROUTE : HPOT->ISP->DTAG->PLUSSERVER-AS->DE:217.118.16.163


        
if __name__ == '__main__' :
       
# Set the input file to scan
    filename = '/home/var/log/tweets.attempts.log.txt'
    file = open(filename,'r')     
                       
    while True:
                               
        line  = file.readline()
        line  = line.rstrip('\n')
                                                                       
        if not line:            # no data to process
            pass
        else :                  # new data has been found
            visTweet(line)
                                                                    
        #time.sleep(0.1)         # 0.1 
                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                  