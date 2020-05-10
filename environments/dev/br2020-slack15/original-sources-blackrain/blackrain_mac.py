#!/usr/local/bin/python
#
# root@m# ifconfig eth0
# eth0  Link encap:Ethernet  HWaddr 00:C0:9F:1B:CA:5E  
#       inet6 addr: fe80::2c0:9fff:fe1b:ca5e/64 Scope:Link
#       UP BROADCAST RUNNING PROMISC MULTICAST  MTU:1500  Metric:1
#       RX packets:853 errors:0 dropped:0 overruns:0 frame:0
#       TX packets:15 errors:0 dropped:0 overruns:0 carrier:0
#       collisions:0 txqueuelen:1000 
#       RX bytes:83547 (81.5 KiB)  TX bytes:1126 (1.0 KiB)
#                                                             
#       root@mars:~# ifconfig eth0 | grep HWaddr
#       eth0      Link encap:Ethernet  HWaddr 00:C0:9F:1B:CA:5E

import os,syslog

def getMacAddress(interface="eth0"):
    cmdLine = "ifconfig " + interface + " | grep HWaddr"
    #print "cmdLine = " + cmdLine 
     
    try:
        pipe = os.popen(cmdLine,'r')
        raw = pipe.read().rstrip("\n")
        #print raw
        start = raw.find("HWaddr")
        if start != -1 :
            mac = raw[start:].split(' ')[1]
            #print '[' + mac + ']'
            return mac
        else:
            return None		# couldn't find mac address
                                                                         
    except Exception,e:
        syslog.syslog("Exception " + `e` + " in getMacAddress(), raw=" + raw);
        return None
                                                                
########
# MAIN #
########        
if __name__ == '__main__': 
    print "\nTest 1"
    mac = getMacAddress()
    print "mac1 = " + `mac`
    
    print "\nTest 2"
    mac = getMacAddress("eth0")
    print "mac2 = " + `mac`
    
    print "\nTest 3"
    mac = getMacAddress("eth1")
    print "mac3 = " + `mac`

    print "\nTest 4"
    mac = getMacAddress("eth2")
    print "mac4 = " + `mac`

    print "\nTest 5"
    mac = getMacAddress("eth3")
    print "mac5 = " + `mac`

    
  