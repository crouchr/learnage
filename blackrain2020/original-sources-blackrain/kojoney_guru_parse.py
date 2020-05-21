#!/usr/bin/python

import syslog
import ipintellib

# add exception handling !!!
def guruTwittify(tweet):
                                                                                                                                                              
    tweet = tweet.replace("dns=NoDNS" , ""  )                                                                           
    return tweet              
                                                                                                                                                                                                                               
# Called from kojoney_tweet.py when a line is found in kojoney_guru.txt
def processguru(line):
  
    try:       
        line = line.rstrip("\n")
        if line.find("GURU") != -1 :	# 
            msg  = line.split(",")	# third fields
            tweet = msg[0] + "," + msg[1]
            tweet = guruTwittify(tweet)
            print "kojoney_guru_parse.py : processguru() : tweet = " + tweet
            return tweet
        else:
            return None

    except Exception,e:
        syslog.syslog("kojoney_guru_parse.py : processguru() : " + `e` + " line=" + line)
                

if __name__ == '__main__' :
    
    filename = '/home/var/log/kojoney_guru.txt'
    file = open(filename,'r')
                
    while True:
        line  = file.readline() 
        tweet = processguru(line)
        
        if tweet != None:
            print "tweet:" + tweet
        
