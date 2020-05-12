#!/usr/bin/python

import syslog

# add exception handling !!!
# works for Snort and Suricata
def broTwittify(tweet):
                                                                                                                                                                  
    # Obfuscate honeypot IPs - this is common to all events so needs to be broken out                                                                                                                                                                                  
    tweet = tweet.replace("172.31.0.67 "  ,  "LINUX->"  )             # High-interaction    Linux   honeypot
    tweet = tweet.replace("192.168.1.66 " ,  "AMUN->"   )             # Medium-interaction  Linux   honeypot
    tweet = tweet.replace("192.168.1.65 " ,  "NEPEN->"  )             # Medium-interaction  Win32   honeypot
    tweet = tweet.replace("192.168.1.64 " ,  "KIPPO->"  )             # Medium-interaction  SSH     honeypot
    tweet = tweet.replace("192.168.1.63 " ,  "HONEYD->" )             # Low-interaction     generic honeypot
    tweet = tweet.replace("192.168.1.62 " ,  "WEB->" )                # Low-interaction     Web     honeypot
                                                                
    return tweet                                                                                                                                                                                                                                         
                                                                                                                                                                                 
                                                                                                                                                                                                          

# does this break if there is not an Xref in the alert ?
def processBroCon(line):
  
    try:
       
        line = line.rstrip("\n")
        #print "bro : " + line
        
        if line.find(" L ") == -1 :	# process locally-originated connections
            return
        fields = line.split()
        #print fields
        
        tweet = "NIDS_BRO_LC," + ' '.join(fields[2:])                                                                        
        tweet = broTwittify(tweet)
        return tweet
        
    except Exception,e:
        syslog.syslog("kojoney_bro_parse.py : processBroCon() : " + `e` + " line=" + line)
                

if __name__ == '__main__' :
    
    filename = '/usr/local/bro/logs/current/conn.log'
    file = open(filename,'r')
                
    while True:
        line  = file.readline() 
        tweet = processBroCon(line)
        
        if tweet != None:
            print "tweet:" + tweet
        
