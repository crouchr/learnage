#!/usr/local/bin/python

import os,syslog,re,logging

# return True if can ping the Internet
def doHaveConnectivity(host="www.google.com"):
    print "[+] Please wait, checking pingability of " + host
    # Check that ARP is working 
    cmdLine = "ping -c2 " + host + " 2>/dev/null"
    logging.info(cmdLine)
    pipe = os.popen(cmdLine,'r')
    
    # The real test
    cmdLine = "ping -c1 " + host
    logging.info(cmdLine)
    pipe = os.popen(cmdLine,'r')
    raw = pipe.read()
    print raw
    
    if raw.find("1 received") != -1:
        logging.info("doHaveConnectivty(" + host +") returns TRUE")
        return True
    else:
        logging.info("doHaveConnectivty(" + host +") returns FALSE")
        return False    

# Return IP address of default gateway
# Return port to use to reach default gateway
def getDGIP():
    
    cmdLine = "netstat -rn"
    #print "cmdLine = " + cmdLine 
             
    try:
        pipe = os.popen(cmdLine,'r')
        raw = pipe.read().rstrip("\n")
        #print raw
        raw=raw.replace("\n"," ")
        raw=raw.replace(" "," ")
        
        #print " "
        #print raw
        
        pat = '0\.0\.0\.0\s*(\d+\.\d+\.\d+\.\d+)\s*0\.0\.0\.0\s*UG\s*0 0\s*0 (.*)'
        
        a = re.findall(pat,raw)
        #print "a=" + a.__str__()
        #print len(a)
        if len(a) != 0 :
            #print "success"
            #print a
            ip    = a[0][0]
            iface = a[0][1]
            return ip,iface
        else :
            syslog.syslog("Failed to identify default gateway")
            return None,None
                                                                                                                                                                            
    except Exception,e:                                    
        syslog.syslog("Exception " + `e` + " in getDGIP(), raw=" + raw);
        return None

# Return MAC address of IP 
#root@mars:/home/crouchr/blackrain_dev# arp -a     
#? (192.168.1.131) at 00:06:4F:59:6E:09 [ether] on eth2
#adsl (192.168.1.254) at 00:14:BF:77:42:B8 [ether] on eth2
#? (192.168.1.248) at 00:21:29:6C:E4:C8 [ether] on eth2
#? (172.29.0.253) at 00:10:DB:7D:F8:0F [ether] on br0
#mail (192.168.1.70) at 00:0C:76:37:CD:8D [ether] on eth2
#root@mars:/home/crouchr/blackrain_dev# 
def getMACip(ip):
    
    # ping the default GW to ensure ARP table is fresh
    cmdLine = "ping -c1 " + ip
    #print "cmdLine = " + cmdLine 
    pipe = os.popen(cmdLine,'r')
        
    cmdLine = "arp -a"
    #print "cmdLine = " + cmdLine 
             
    try:
        pipe = os.popen(cmdLine,'r')
        raw = pipe.read().rstrip("\n")
        #print raw
        raw=raw.replace("\n"," ")
        raw=raw.replace(" "," ")
        
        #print " "
        #print raw
        
        pat = '\(' + ip + '\)' + ' at (\w\w:\w\w:\w\w:\w\w:\w\w:\w\w)'
        #print "pat=" + `pat`
        a = re.findall(pat,raw)
        if a != None:
            #print a
            return a[0]
        else :
            return None
        
                                                                                                                                                                            
    except Exception,e:                                    
        syslog.syslog("Exception " + `e` + " in getMACip(), raw=" + raw);
        return None
                                                                                                                                          

########           
# MAIN #           
########           

if __name__ == '__main__':

    dgIP,dgIF = getDGIP()
    if dgIP != None and dgIF != None:
        print "Default Gateway IP is " + dgIP
        print "Default Gateway is reachable via " + dgIF
        
    dgMAC = getMACip(dgIP)
    if dgMAC != None :
        print "Default Gateway MAC is " + dgMAC
                                             