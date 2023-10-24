#!/usr/bin/python

import time, os , syslog , re 
#import kojoney_afterglow
import blackrain_netflow
import kojoney_hiddenip

def twittifyNetflow(tweet):
    print "kojoney_netflow_parse.py : twittifyHoneyd() : before twittification, raw tweet = " + tweet
                                                                                                                            
    # Honeyd - protocol normalisation        
    #tweet = tweet.replace("tcp(6)"  , "T")
    #tweet = tweet.replace("udp(17)" , "U")
    #tweet = tweet.replace("icmp(1)" , "I")
    
    tweet = tweet.replace("tcp(6)"  , "tcp")
    tweet = tweet.replace("udp(17)" , "udp")
    tweet = tweet.replace("icmp(1)" , "icmp")
    tweet = tweet.replace("tx=0"    , "")
    tweet = tweet.replace("rx"      , "rxBytes")
    tweet = tweet.replace("Windows" , "Win32")

    tweet = tweet.replace("192.168.1.63 ",  "[NETFLOW] " ) 
        
    print "kojoney_netflow_parse.py : twittifyNetflow() : after twittification, raw tweet = " + tweet                                                                                                                                                                   
    
    return tweet                                                                                                                                                                                     
                                                                                                                                                                                                            
#Aug 16 12:46:35 mars blackrain_netflow: dir=in sIP=187.33.4.81 sP=60345 dIP=192.168.1.64 dP=2222 pr=6 B=1100 p=11 fl=27 t=3423
#Aug 16 12:46:35 mars blackrain_netflow: dir=in sIP=187.33.4.81 sP=60094 dIP=192.168.1.64 dP=2222 pr=6 B=1220 p=12 fl=27 t=4064
#Aug 16 12:46:35 mars blackrain_netflow: dir=out sIP=192.168.1.64 sP=2222 dIP=187.33.4.81 dP=60345 pr=6 B=1672 p=12 fl=27 t=3136
#Aug 16 12:46:45 mars blackrain_netflow: dir=in sIP=187.33.4.81 sP=60579 dIP=192.168.1.64 dP=2222 pr=6 B=1324 p=13 fl=27 t=9988
#Aug 16 12:46:45 mars blackrain_netflow: dir=out sIP=192.168.1.64 sP=2222 dIP=187.33.4.81 dP=60579 pr=6 B=1952 p=14 fl=27 t=9714
#Aug 16 12:56:30 mars blackrain_netflow: dir=in sIP=218.80.254.242 sP=13924 dIP=192.168.1.64 dP=2222 pr=6 B=88 p=2 fl=6 t=4089
#Aug 16 12:56:30 mars blackrain_netflow: dir=out sIP=192.168.1.64 sP=2222 dIP=218.80.254.242 dP=13924 pr=6 B=96 p=2 fl=18 t=3604
#Aug 16 13:08:25 mars blackrain_netflow: dir=out sIP=192.168.1.66 sP=445 dIP=81.88.159.15 dP=4499 pr=6 B=128 p=3 fl=19 t=318
#Aug 16 13:08:30 mars blackrain_netflow: dir=in sIP=81.88.159.15 sP=4499 dIP=192.168.1.66 dP=445 pr=6 B=168 p=4 fl=19 t=500
#Aug 16 13:08:30 mars blackrain_netflow: dir=out sIP=192.168.1.66 sP=445 dIP=81.88.159.15 dP=4504 pr=6 B=1770 p=12 fl=26 t=4790
#Aug 16 13:08:30 mars blackrain_netflow: dir=in sIP=81.88.159.15 sP=4535 dIP=192.168.1.66 dP=139 pr=6 B=487 p=7 fl=27 t=953
#Aug 16 13:08:30 mars blackrain_netflow: dir=in sIP=81.88.159.15 sP=4504 dIP=192.168.1.66 dP=445 pr=6 B=2947 p=14 fl=26 t=5111
#Aug 16 13:08:30 mars blackrain_netflow: dir=out sIP=192.168.1.66 sP=139 dIP=81.88.159.15 dP=4535 pr=6 B=600 p=6 fl=27 t=773
#Aug 16 13:10:30 mars blackrain_netflow: dir=out sIP=192.168.1.66 sP=445 dIP=81.88.159.15 dP=4504 pr=6 B=40 p=1 fl=17 t=0
# return the Tweet or None

# field[0] = 'May'
# fields = ['May', '19', '07:19:18', 'mars', 'blackrain_netflow:', 'netflow_record', 'dir=out', 'sIP=192.168.1.60', 
# 'sP=8085', 'dIP=58.218.199.250', 'dP=12200', 'pr=6', 'B=40', 'p=1', 'fl=20', 't=0']


def processNetflow(line):

#    global p0f

    flowEvent = {}
    tweet = None
    
    # parsing is broken - do nothing until it is fixed - use code from blackrain_netflow.py
    #return None,flowEvent
 
    try :
        line = line.rstrip("\n")
        print "kojoney_netflow_parse.processNetflow() : line read is " + line
                
        # For BRX, do not insist that data was sent - easier to test with ShieldsUp!
        #if line.find("192.168.1.63") != -1 and line.find("END") != -1 :
        flowEvent = blackrain_netflow.processNetflow(line)
        #print flowEvent
        
        # Do not tweet netflows
        return None,flowEvent	
        
        # Not interested in SYN scanners - ignore
        #if line.find("fl=2 ") != -1 :
        #    return None,flowEvent
        #  
        ## only want outgoing flows - looking for flows initiated by the honeypot
        ##if line.find("dir=out ") == -1 :
        ##    return None,flowEvent
        #
        #fields = line.split(" ")
        #print fields
        #print fields[0]
        #
        #msecs = fields[15].split("=")[1]        
        #print "msecs=" + msecs
        #if int(msecs) <= 1000 :		# flow must be longer than 1 second
         #   return None,flowEvent
        
        #packets = fields[13].split("=")[1]
        #print "packets=" + packets
        #if int(packets) <= 3 :			# flow must be longer than 3 packets
        #    return None,flowEvent

        #bytes = fields[12].split("=")[1]
        #print "bytes=" + bytes

        # only interesting tweets
        # do not want the ephermeral port numbers or correlation will not weed out repeat flows
        # need to refine this to extract the port number in a smart way
        #if int(msecs) >= 1000 or int(packets) >= 10 or int(bytes) >= 1024 :
        #    dir  = fields[5]
        #    sIP  = fields[7]	# sIP
        #    sP   = fields[8]
        #    dIP  = fields[9]
        #    dP   = fields[10]    # dP
        #    pr   = fields[11]   # protocol
        #    #dIP  = fields[7]
        #    #sP   = fields[6]
        #    
        #    print dir + " " + sIP + " " + sP + " -> " + dIP + " " + dP + " " + pr + " " + bytes
        #    tweet = "NETFLOW," + dir + " " + dIP + " " + pr
        #    
        #    if kojoney_hiddenip.hiddenIP(dIP) == False:
        #        # Tweet does not contain unwanted IP addresses
        #        print tweet
        #        return tweet,flowEvent
        #    else:
        #        return None,flowEvent
        #    
        #else:
        #    return None,flowEvent
        
    except Exception,e:
        msg = "kojoney_netflow_parse.py : processNetflow() : " + `e` + " line=" + line
        syslog.syslog(msg)
        print msg
        return None,flowEvent

# TEST HARNESS
if __name__ == '__main__' :
    print "Started"
# Set the input file to scan
    filename = '/home/var/log/netflow.syslog'
    #filename = 'honeyd.syslog.test'
    file = open(filename,'r')
                
    while True:               
        line = file.readline()
        line = line.rstrip('\n')
                                                                
        if not line:            # no data to process
            pass
        else :                  # new data has been found
            print "---------------"
            print "Found a netflow record to process " + line
            tweet,flowEvent = processNetflow(line)
        
        # print out tweets that would actually get tweeted                                                                                                                            
        if tweet != None and tweet.find(":::") == -1 :
            print "*** tweet : " + tweet
            print "*** flow  : " + flowEvent.__str__()
                                                                                                                                                                               
        time.sleep(0.1)         # 0.1 
                                                                                                                                                                                                            