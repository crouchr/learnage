#!/usr/bin/python

import time, os , syslog , re 
import kojoney_afterglow
import blackrain_honeyd

def twittifyHoneyd(tweet):
    #print "kojoney_honeyd_parse.py : twittifyHoneyd() : before twittification, raw tweet = " + tweet
                                                                                                                            
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

    tweet = tweet.replace("192.168.1.63 ",  "[HONEYD] dport=" )         # Low-interaction generic honeypot
    tweet = tweet.replace(" END",  "")
    
    #print "kojoney_honeyd_parse.py : twittifyHoneyd() : after twittification, raw tweet = " + tweet                                                                                                                                                                   
    
    return tweet                                                                                                                                                                                     
                                                                                                                                                                                                            

#2011-01-11:23-55-19:udp(17):END:192.168.1.240 123 192.168.1.166 123:rx=48:tx=0:
# return the Tweet or None
p0f = {}
def processHoneyd(line):

    global p0f

    flowEvent = {}
    tweet = None
    
    if line.find(" arp reply") != -1 :
        return None,flowEvent
    
    # fix bug when date is 1-9 of month    
    line = line.replace("  "," ")	# replace double space with one space
    #line = line.rstrip("\n")
    #line = line.rstrip(" ")
        
    try :
        print "kojoney_honeyd_parse.processHoneyd() : line read is " + line
            
        # only honeyd "START" messages have p0f info in them
        pat = "genre=([A-Za-z0-9]*)"
        a = re.findall(pat,line)
        if len(a) != 0 :
            genre = a[0]
            #print "genre=" + genre
            pat = r'\d+\.\d+\.\d+\.\d+'             # locate a number of IP addresses
            ips = re.findall(pat,line)
            if len(ips) != 0 :
                ip = ips[0]
                p0f[ip] = genre
                #print "p0f cache for " + ip + " set to [" + genre + "]"                        
            
            #pat = "signature match: \"([A-Za-z0-9 ]*)\""
            #a = re.findall(pat,line)
            
        # Honeyd log must be related to the Honyed virtual IP and must be a session log ("END") 
        # and there must have been actual data received by honeyd for the log to be Tweeted
        #if line.find("192.168.1.63") != -1 and line.find("END") != -1 and line.find("rx=0") == -1 :
        if line.find("192.168.1.63") != -1 and line.find("END") != -1 and line.find("rx=0") == -1 :
            #print line
            fields = line.split(":")
            #print "->"
            #print fields
            msg    = ' '.join(fields[5:])		# this one
            msg    = msg.rstrip("\n")			# remove bogus trailing \n
            msg    = msg.rstrip(" ")			# remove bogus trailing SPACE
            #print "kojoney_honeyd_parse.processHoneyd() : shortened msg = " + msg
            
            # Append OS
            pat = r'\d+\.\d+\.\d+\.\d+'             	# locate a number of IP addresses
            ips = re.findall(pat,line)
            if len(ips) != 0 :
                sip = ips[0]

            if p0f.has_key(sip) :
                genre = "os=" + p0f[sip]
            else:
                genre = ""    
            msg = msg + genre
            
            tweet  = "HONEYD_FLOW," + msg
            #print tweet
    
            #print "processHoneyd() : fields=" + `fields`
            
            fields = line.split(" ")
            #print "-->"
            #print fields
            
            dport = fields[8].split(":")[0]
            rx    = fields[8].split(":")[1]
            rx    = rx.split("=")[1]
            #print "dport found : " + dport
            #print "rx found    : " + rx
            
            tweet  = twittifyHoneyd(tweet)
            
            # Now have correlation so minimise dropping of Tweets
            # do no tweet "expected ports"
            #if dport=="1433" or dport=="4899":
            #    tweet = tweet + ":::"
                
            # do not tweet sessions with less than 10 bytes data exchanged
            # have also set this to 20 in the past
            if int(rx) < 10 :    
                tweet = tweet + ":::"

            kojoney_afterglow.visHoneyd(tweet)
               
            #return tweet,flowEvent
        
        # For BRX, do not insist that data was sent - easier to test with ShieldsUp!
        if line.find("192.168.1.63") != -1 and line.find("END") != -1 :
            flowEvent = blackrain_honeyd.processHoneyd(line)
            #print flowEvent
        
        return tweet,flowEvent
        
        print "Honeyd flow is not interesting, so ignore"
        return None,flowEvent


    except Exception,e:
                syslog.syslog("kojoney_honeyd_parse.py : processHoneyd() : " + `e` + " line=" + line)


if __name__ == '__main__' :

# Set the input file to scan
    filename = '/home/var/log/honeyd.syslog'
    #filename = 'honeyd.syslog.test'
    file = open(filename,'r')
                
    while True:               
        line = file.readline()
        line = line.rstrip('\n')
                                                                
        if not line:            # no data to process
            pass
        else :                  # new data has been found
            tweet,flowEvent = processHoneyd(line)
        
        # print out tweets that would actually get tweeted                                                                                                                            
        if tweet != None and tweet.find(":::") == -1 :
            print "*** tweet : " + tweet
            print "*** flow  : " + flowEvent.__str__()
                                                                                                                                                                               
        time.sleep(0.1)         # 0.1 

                                                                                                                                                                                                                                                        