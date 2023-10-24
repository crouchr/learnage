#!/usr/bin/python
import os,time,syslog,sys
import kojoney_hiddenip
import ipintellib 
import twitter_funcs
import kojoney_blackhole_idmef
import kojoney_attacker_event

# Only use syslog() for errors

BlackholedRoutes = {}
BH_DURATION = 600 		# secs
BH_DURATION = 120 		# secs
    
# inject a blackhole route
# return Tweet
def blackhole(txnId,sensorId,attacker):
    global BlackholedRoutes
    global BH_DURATION
        
    try :
        # do not blackhole items on whitelist
        print "*** kojoney_defend.py : calling hiddenIP() ***"
        if kojoney_hiddenip.hiddenIP(attacker) == True :
            msg = "kojoney_defend.py : blackhole() : warning : attacker " + attacker + " is on hiddenIP() whitelist and must not be blackholed"
            print msg
            syslog.syslog(msg)
            return None
            
        # blackhole route already exists - issue - should the time be reset to zero ?         
        #if BlackholedRoutes.has_key(attacker) == True :
        #    return None
            
        # get hostname of the attacker
        dnsInfo = ipintellib.ip2name(attacker)
        dnsName = dnsInfo['name']
        
        # inject the blackhole
        cmd = "/sbin/ip route add blackhole " + attacker
        msg = "Added blackhole (" + BH_DURATION.__str__() + "s) on " + time.ctime() + " for " + attacker + " " + dnsName.__str__()
        #print msg
        #syslog.syslog(msg)

        # Update Attacker Database
        srcIP = attacker
        kojoney_attacker_event.generateAttackerEvent(txnId,srcIP,None,sensorId,"BHOLE","DEFEND",None,"Attacker blackholed",None,None,None,None,None)

        kojoney_blackhole_idmef.sendBlackholeIDMEF(attacker,"Added blackhole")
                
        pipe = os.popen(cmd,'r')
        tweet = "DEFEND," +  msg 
        
        #return None	# do not Tweet - not interesting to average punter
        return tweet
                                                                                     
    except Exception,e:
        msg = "kojoney_defend.py : blackhole() exception caught = " + `e`
        syslog.syslog(msg)
        print msg
        return None
                  
                                                                                                                                                                         
def ageBlackholedRoutes(bh_duration):
    global BlackholedRoutes
    
    try :
        agedAttackers = []
        now = time.time()
        #print now
        for attacker in BlackholedRoutes :
            blackholeBorn = BlackholedRoutes[attacker]
            blackholeAge  = now - blackholeBorn
            #print " -> blackholeAge for " + attacker + " is " + blackholeAge.__str__() + " seconds"
            if blackholeAge > bh_duration :
                print attacker + " has now aged out"
                agedAttackers.append(attacker)
                #del BlackholedRoutes[attacker]
                
                cmd = "/sbin/ip route delete blackhole " + attacker
                
                # get hostname of the attacker
                dnsInfo = ipintellib.ip2name(attacker)
                dnsName = dnsInfo['name']
                
                msg = "Removed blackhole on " + time.ctime() + " for " + attacker + " " + dnsName.__str__()
                #print msg
                #syslog.syslog(msg)
                kojoney_blackhole_idmef.sendBlackholeIDMEF(attacker,"Removed blackhole")
                
                pipe = os.popen(cmd,'r')
                raw = pipe.read().rstrip("\n")
                
                tweet = "DEFEND," + msg
                # Do not Tweet - not very interesting
                twitter_funcs.addTweetToQueue(tweet,geoip=True)
                
        for attacker in agedAttackers:
            del BlackholedRoutes[attacker] 
            #print "attacker " + attacker + " removed from list of blackholes"
    
    except Exception,e:
        msg = "kojoney_defend.py : ageBlackholedRoutes() exception caught = " + `e`
        syslog.syslog(msg)
        print msg
        #sys.exit()         
  
# add new blackholes to dictionary    
def getRouteTable():
    #global ProcessTable

    try :
    #BlackholedRoutes = {}	# zero the process table
    
        os.system("netstat -rn > /tmp/routeTable.txt")
        file = open("/tmp/routeTable.txt",'r')
        
        while True:
            line = file.readline()
            line = line.strip()
            if not line :  
                #print "No (more) data to read"
                break
        
            #print "line is : " + line     
            #fields = line.split()
            #print fields
            
            if line.find("0.0.0.0") >= 0 and line.find("*") >= 0 :	# found blackhole route
                attacker = line.split(" ")[0]
                #print line
                #print "attacker is " + "[" + attacker + "]"

                if BlackholedRoutes.has_key(attacker) == False : # attacker not seen before
                    print "new blackhole route added to monitor list " + attacker 
                    BlackholedRoutes[attacker] = time.time()
                         
             
    except Exception,e:
        msg = "kojoney_defend.py : getRouteTable() exception caught = " + `e`
        syslog.syslog(msg)
        print msg
        #sys.exit()         
  
syslog.openlog("kojoney_defend",syslog.LOG_PID,syslog.LOG_LOCAL2)         # Set syslog program name 

if __name__ == "__main__" :

    #BH_DURATION = 600 		# secs
    #print "BH_DURATION : " + BH_DURATION.__str__()
    
    while True:
        try:    
            # scan route table and add to dictionary
            getRouteTable()
            #print "blackhole route table : " + BlackholedRoutes.__str__()

            # ageout old blackhole routes
            ageBlackholedRoutes(BH_DURATION)
        
            #print " "
            time.sleep(10)
    
        except Exception,e:
            msg = "kojoney_defend.py : main() exception caught = " + `e`
            print msg
            syslog.syslog(msg)
            sys.exit()
   
