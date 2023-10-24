#!/usr/bin/python

import syslog
import re

# add exception handling !!!
def routerTwittify(tweet):
                                                                                                                                                                  
    # Obfuscate honeypot IPs - this is common to all events so needs to be broken out                                                                                                                                                                                  
    tweet = tweet.replace("-> 192.168.1.9" ,  "-> RTR" )   
    tweet = tweet.replace("packet"         ,  "pkt" )   
    tweet = tweet.replace("packets"        ,  "pkts" )   
    tweet = tweet.replace(" list "         ,  " " )   
    tweet = tweet.replace("permitted"      ,  "permit" )   

    #ICMPv6 - See Configuring IPv6 for Cisco IOS book page 71
    tweet = tweet.replace(" (128/0)"   ,  "(PING)"  )   
    tweet = tweet.replace(" (129/0)"   ,  "(REPLY)" )   
    tweet = tweet.replace(" (133/0)"   ,  "(RS)"    )   
    tweet = tweet.replace(" (134/0)"   ,  "(RA)"    )   
    tweet = tweet.replace(" (135/0)"   ,  "(NS)"    )   
    tweet = tweet.replace(" (136/0)"   ,  "(NA)"    )   

    #tweet = tweet.replace(" -> "       ,  "->"      ) 
    
    #tweet = tweet.replace("192.168.1.66 " ,  "AMN->"  )             # Medium-interaction  Linux   honeypot
    #tweet = tweet.replace("192.168.1.65 " ,  "NEP->"  )             # Medium-interaction  Win32   honeypot
    #tweet = tweet.replace("192.168.1.64 " ,  "KIP->"  )             # Medium-interaction  SSH     honeypot
    #tweet = tweet.replace("192.168.1.63 " ,  "HYD->"  )             # Low-interaction     generic honeypot
                                                                
    return tweet                                                                                                                                                                                                                                         


# Tweet interesting honey router syslog events
# Do not Tweet if source IP is in 192.168.1.0.0/24
# IPv4 
def processrouter(line):
    try:       
        
        if line.find(": %") == -1 :
            return

        if line.find("SYS-3-CPUHOG") != -1 :
            return

        
        line = line.rstrip("\n")
            
        fields = line.split()
        if len(fields) < 4:
            return None
            
        #print fields
        
        #p = fields[5].split(":")[0]
        #    tweet = "p0f_LINK," + "ip=" + ip + " link=GPRS|T1|FreeS/WAN" + " " + prettyAS(ip)
        #    tweet = p0fTwittify(tweet)
        tweet = ' '.join(fields[9:])
        tweet = routerTwittify(tweet)
        
        # ignore debug messages i.e. anything with %
        #print "tweet1=" + tweet
        #if tweet.find(": %") == -1 :
        #    return
        
        #print tweet        
        pat = r'\d+\.\d+\.\d+\.\d+'             # locate a number of IP addresses
        ips = re.findall(pat,tweet)  
        #print len(ips)
        if len(ips) != 0 :
            srcIP = ips[0]
            #print "source IP is " + srcIP                                 
            if srcIP.find("192.168.") != -1 :	# Don't tweet locally-sourced packets
                return None       
                 
        tweet = "RTR_LOG," + tweet
        #print "processrouter() : tweet = " + tweet        
        return tweet
        
    except Exception,e:
        syslog.syslog("kojoney_router_parse.py : processrouter() : " + `e` + " line=" + line)

# Tweet interesting honey router syslog events
# Do not Tweet if source IP is in 192.168.1.0.0/24
# IPv4 
def processrouterv6(line):
    try:       
        
        if line.find(": %") == -1 :
            return

        if line.find("SYS-3-CPUHOG") != -1 :
            return
        
        line = line.rstrip("\n")
            
        fields = line.split()
        if len(fields) < 4:
            return None
            
        #print fields
        
        tweet = ' '.join(fields[10:])
        tweet = routerTwittify(tweet)
        
        tweet = "RTRv6_LOG," + tweet
        #print "processrouterv6() : tweet = " + tweet        
        
        return tweet
        
    except Exception,e:
        syslog.syslog("kojoney_router_parse.py : processrouterv6() : " + `e` + " line=" + line)
                
if __name__ == '__main__' :
    
    filename = '/home/var/log/honeyrtr.syslog'
    #filename = '/home/var/log/honeyrtrv6.syslog'
    file = open(filename,'r')
                
    while True:
        line  = file.readline() 
        tweet = processrouter(line)
        #tweet = processrouterv6(line)
        
        if tweet != None:
            print "tweet:" + tweet
        
