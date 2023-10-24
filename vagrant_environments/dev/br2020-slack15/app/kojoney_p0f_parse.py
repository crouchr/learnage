#!/usr/bin/python

import syslog,re
import ipintellib
import time

# add exception handling !!!
# works for Snort and Suricata
def p0fTwittify(tweet):
                                                                                                                                                                  
    # Obfuscate honeypot IPs - this is common to all events so needs to be broken out                                                                                                                                                                                  
    tweet = tweet.replace("172.31.0.67 "  ,  "LNX->"  )             # High-interaction    Linux   honeypot
    tweet = tweet.replace("192.168.1.66 " ,  "AMN->"  )             # Medium-interaction  Linux   honeypot
    tweet = tweet.replace("192.168.1.65 " ,  "NEP->"  )             # Medium-interaction  Win32   honeypot
    tweet = tweet.replace("192.168.1.64 " ,  "KIP->"  )             # Medium-interaction  SSH     honeypot
    tweet = tweet.replace("192.168.1.63 " ,  "HYD->"  )             # Low-interaction     generic honeypot
                                                                
    return tweet                                                                                                                                                                                                                                         

# make this a common fn in ipintellib and add try: handling
def prettyAS(ip):                                                                                                                                                                                 
    asMsg = ""
    if ip != None:
        #print "prettyAS() : IP found = " + ip
        # WHOIS information
        asInfo = ipintellib.ip2asn(ip)
        asNum =  asInfo['as']                                   # AS123 
        asRegisteredCode = asInfo['registeredCode']             # Short-form e.g.ARCOR
        asMsg = asRegisteredCode + " (" + asNum + ")"
    
    #print "AS info : " + asMsg     
    return asMsg                                                                                                                                                                                                                                                                                                                                   

# Tweet intersting p0f events
# todo : tweet if os <> {Linux Windows Novell UNKNOWN} i.e openbsd , freebsd etc.
# this needs correlation to remove large numbers of events if a scan occurs
# it also needs destination port so that OS can be deduced
def processp0f(line):
   
    #print "p0f:" + line.rstrip('\n')
    #return None			# fires too often if an SSH brute force - need correlation
        
    pat = 'up: (\d+)'             # locate a number of IP addresses
    a = re.findall(pat,line)
    if len(a) != 0 :
        uptime = int(a[0])
    else:
        return None
    
    #print "uptime  = " + `uptime`     
    now = time.time()
    nowLocal = time.localtime(now)
    #print "now     = " + `now`
    
    boot = now - uptime
    #print "-> boot = " + `boot`
    
    tuple=time.gmtime(boot)
     
    bootTstamp = "%02d" % tuple.tm_hour + ":" + "%02d" % tuple.tm_min + ":" + "%02d" % tuple.tm_sec + " " + "%02d" % tuple.tm_mday + "/" + "%02d" % tuple.tm_mon + "/" + "%04d" % tuple.tm_year    
    #print bootTstamp
    
    pat = '\d+\.\d+\.\d+\.\d+'             # locate a number of IP addresses
    pat = '\d+\.\d+\.\d+\.\d+:\d+'         # locate a number of IP:port patterns
    a = re.findall(pat,line)
    if len(a) != 0:
        srcIP = a[0]
        dstIP = a[1]
        #print "srcIP = " + srcIP
        #print "dstIP = " + dstIP
        
        # Do not create messages for honeypot system itself
        if srcIP.find("192.168.1.67") != -1 :
            #print "Do not process p0f for botwall itself"
            return None
        
        #msg = time.asctime(nowLocal)
        msg = srcIP + " -> " + dstIP + " now=" + `now` + " uptime=" + `uptime` + " -> boot=" + `boot` + " bootTstamp=" + bootTstamp
        
        fp = open("/home/var/log/uptimes.log",'a')
        print >> fp,msg
        fp.close()
        
        tweet = "p0f_UP," + msg
        #print tweet
        
        return None	# do not create Tweet until i have some correlation -  too many events if a SSH brute force scan for example
        return tweet
#now = time.time()
#twitter_geoip.py:        nowLocal = time.gmtime(now)
#twitter_geoip.py:        alertContent = content + "\n\nSent by Kojoney Honeypot on " + time.asctime(nowLocal) + "\n\n"  
 
 # work in progress - something wrong with the p0f uptime calculation ?
        
    return None
  
    try:       
        line = line.rstrip("\n")
        if line.find("link: GPRS") != -1 :	# 
            fields = line.split()
            ip = fields[5].split(":")[0]
            #os = fields[7]
            #print "ip=" + ip
            #print "os=" + os
            #print fields
            #tweet = "p0f_LINK," + "ip=" + ip + " os=" + os + " link=GPRS/T1/FreeS/WAN" + " " + prettyAS(ip)
            #tweet = "p0f_LINK," + "ip=" + ip + " link=GPRS|T1|FreeS/WAN" + " " + prettyAS(ip)
            tweet = "p0f_LINK," + "ip=" + ip + " link=GPRS|T1|FreeS/WAN"
            tweet = p0fTwittify(tweet)
            return tweet
        elif line.find("link: IPv6") != -1 :	# 
            fields = line.split()
            ip = fields[5].split(":")[0]
        #    os = fields[7]
        #    #print "ip=" + ip
        #    #print "os=" + os
        #    #print fields
            tweet = "p0f_LINK," + "ip=" + ip + " link=IPv6/IPIP"
            tweet = p0fTwittify(tweet)
            return tweet
        #elif line.find("Masquerade at") != -1 :	# not that interesting it seems	 
        #    fields = line.split()
        #    ip = fields[8].split(":")[0]
        #    #print "ip=" + ip
        #    #print fields
        #    tweet = "p0f_MASQ," + "masquerade detected at ip=" + ip
        #    tweet = p0fTwittify(tweet)
        #    return tweet
        else:
            return None
    except Exception,e:
        syslog.syslog("kojoney_p0f_parse.py : processp0f() : " + `e` + " line=" + line)
                

if __name__ == '__main__' :
    
    filename = '/home/crouchr/p0f.log.test'
    file = open(filename,'r')
                
    while True:
        line  = file.readline() 
        tweet = processp0f(line)
        
        if tweet != None:
            print "tweet:" + tweet
        
