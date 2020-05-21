#!/usr/bin/python


import time, os , syslog , re     
    
Correlate = {}

# Twitter correlation
# Return True if message matches a correlation rule
# count = maximum number of events permitted
# Do not correlate if not IP address is found
def correlate(tweet,count):
    global Correlate
    
    # List of eventTypes that should not be subjected to correlation
    notCorrelateEventTypeList = ['LMD','DEFEND','REPORT','AFLOW_OUT','PADS_INET_SERVER','PADS_ANOMALY','CLAMD']
    notCorrelateStringList    = ['BOTJUICER']
    
    # ":::" in the Tweet means do not Tweet it, so do not count it against this IPs count
    if tweet.find(":::") != -1 :
        return 0
    
    # locate IP address
    pat = r'\d+\.\d+\.\d+\.\d+'     	        # locate a number of IP addresses
    ips = re.findall(pat,tweet)     
    
    if len(ips) <= 0:				# can't find an IP address, so can't correlate
        return 0
    else:					# found an IP address
        ip = ips[0]

    fields = tweet.split(",")
    eventType = fields[0]

    # Do not correlate if certain magic strings are in Tweet
    for i in notCorrelateStringList :
        if i.upper() in tweet.upper() :
            return 0

    # Do not correlate certain eventTypes
    for i in notCorrelateEventTypeList :
        if i.upper() in eventType.upper() :
            return 0
            
    # The key for correlation is the eventType e.g.WEB_SCN, REPORT etc.
    event = eventType + ":" + ip
     
    if Correlate.has_key(event) == True :		
        Correlate[event] = Correlate[event] + 1                                                                                                                       
    else:					# first time IP has been seen
        Correlate[event] = 1                       
                                                                                                                                                        
    #if Correlate[event] > count :
    #    print event + " -> correlation, so now suppressing..."
    
    return Correlate[event]    

                                   
# -------------------------------------------------------
        
if __name__ == '__main__' :

    filename = '/home/var/log/tweet_queue.log' 			# real file
    file     = open(filename,'r')
            

    print "system     : Seek to end of Tweets queue " + filename

    try:

        while True:
                   
            line  = file.readline().rstrip()
            print "\n-----------------"
            if not line :		# no data to process
                sys.exit("no more data to process\n")
            else:
                print line                    
                tweet = line.split("tweet=")[1]
                tweet = tweet.strip('"')
                #print "tweet = " + tweet
                count = 3
                a = correlate(tweet,count)
                
                if a == 0:
                    tweet = "<" + `a` + ">" + tweet	# Tweet is exempt from correlation
                    print tweet
                elif a == count :
                    tweet = "[" + `a` + "]" + tweet	# last time Tweet will be printed
                    print tweet
                elif a < count :
                    tweet = "{" + `a` + "}" + tweet    
                    print tweet 
                else :
                    print "Suppressed"
                            
            #time.sleep(0.4)		# use 0.2 secs

    except Exception,e:    
        print "kojoney_correlate.py : main() exception caught = " + `e` + " line=" + line
        #syslog.syslog("kojoney_tweet_engine.py : main() exception caught = " + `e` + " line=" + line)
