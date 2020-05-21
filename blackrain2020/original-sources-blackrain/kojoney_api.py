#!/usr/bin/python
import os,time,syslog,sys
import pickle 		# shelve does not work with bb_freeze
import operator

import kojoney_tsom	# use the odd function in that module

#def orderFlags():
#    try:
#        myorder = 
#    except Exception,e:
#        msg = "kojoney_api.py : orderFlags() : exception : " + e.__str__() 
#        syslog.syslog(msg)
#        print msg
#        return None
    

# dump current state of attackers/attacks to TTY in descending order of CTL
# make this the master and usable form other python files / modules
def dumpTTYattackerDict(ATTACKER_INFO):
    try:
        BLACKLIST = ['192.168.1.73','192.168.1.74','192.168.1.254']	# Do not include any honeypot IPs
        X = {}
        numIPs = 0
        highLineDisplayed = False
        medLineDisplayed  = False        
        
        if len(ATTACKER_INFO) <= 0 :
            print "dumpTTYattackerDict() : No attackers to dump information for, so early return"
            return
        
        for ip in ATTACKER_INFO:
            #print "RT : " + ip + " (" + ATTACKER_INFO[ip]['rdns'] + ")" + " CTL=%.1f" % ATTACKER_INFO[ip]['ctlSum'] + " " + ATTACKER_INFO[ip]['os'] + " (" + ATTACKER_INFO[ip]['cc'] + "," + ATTACKER_INFO[ip]['city'] + ")" + " %.2fN" % ATTACKER_INFO[ip]['latitude'] + " %.2fE" % ATTACKER_INFO[ip]['longitude'] + " " + ATTACKER_INFO[ip]['as'] + " " + ATTACKER_INFO[ip]['isp'] + " (P2 #W=" + ATTACKER_INFO[ip]['weightSum'].__str__() + " P2 #E=" + ATTACKER_INFO[ip]['eventsSum'].__str__() +")" 
            X[ip] = ATTACKER_INFO[ip]['ctlSum']
        
        # Sort based on ctl value, highest at head of list
        SORTED_LIST = sorted(X.iteritems(), key = operator.itemgetter(1), reverse=True)
        #print "Unsorted : " + X.__str__()    
        #print "Sorted   : " + SORTED_LIST.__str__()    
        
        # Count the number of attackers
        for a in SORTED_LIST:
            ip = a[0]
            if ip in BLACKLIST :		# ignore own LAN
                continue     
            numIPs = numIPs + 1
        
        # Display in order of CTL (descending) - leave in .180 (MAC) for testing
        print " "
        print "----------------------------------"
        print "Displaying data for " + numIPs.__str__() + " attacker(s)"
        print "----------------------------------"
        print time.ctime()
        print " "   
        print "--- H I G H ---"     
        for a in SORTED_LIST:
            ip = a[0]
            if ip in BLACKLIST:	# ignore own LAN
                continue  
            if int(ATTACKER_INFO[ip]['ctlSum']) < 6 and highLineDisplayed == False:
                print " "
                print "--- M E D I U M ---" # + ATTACKER_INFO[ip]['ctlSum'].__str__() 
                highLineDisplayed = True
            if int(ATTACKER_INFO[ip]['ctlSum']) < 3 and medLineDisplayed == False:
                print " "
                print "--- L O W ---" # + ATTACKER_INFO[ip]['ctlSum'].__str__() 
                medLineDisplayed = True
            
            if int(ATTACKER_INFO[ip]['ctlSum']) >= 3 : # only High and Medium            
                print "%-15s" % ip + " " + "%4s" % ATTACKER_INFO[ip]['cc'] + " %5s" % ATTACKER_INFO[ip]['os'] + " %7s" % ATTACKER_INFO[ip]['as'] + " %4.1f" % ATTACKER_INFO[ip]['ctlSum'] + " %4.1f" % ATTACKER_INFO[ip]['ctlPeak'] + "^" + " [" + kojoney_tsom.orderFlags(ATTACKER_INFO[ip]['flags']).rstrip(" ") +"]" + " (" + ATTACKER_INFO[ip]['rdns'] + ")" + " " + ATTACKER_INFO[ip]['city'] + " %.2fN" % ATTACKER_INFO[ip]['latitude'] + " %.2fE" % ATTACKER_INFO[ip]['longitude'] + " " + ATTACKER_INFO[ip]['isp'] + " (P2 Weight=" + ATTACKER_INFO[ip]['weightSum'].__str__() + " P2 Events=" + ATTACKER_INFO[ip]['eventsSum'].__str__() +")" 
                print "    LAST -> " + ATTACKER_INFO[ip]['lastSensorTime'] + " sensor=" + ATTACKER_INFO[ip]['lastSensor'] + " sensorMsg=" + ATTACKER_INFO[ip]['lastSensorMsg'] + " addInfo1=" + ATTACKER_INFO[ip]['lastSensorAddInfo1'] + " addInfo2=" + ATTACKER_INFO[ip]['lastSensorAddInfo2'] 
                #print "   epoch=" + time.ctime(float(ATTACKER_INFO[ip]['epoch']))
             
        print " "
            
    except Exception,e:
        msg = "kojoney_api.py : dumpAttackerDict() : exception : " + e.__str__() 
        syslog.syslog(msg)
        print msg
        return
        
# wrapper so can trap exceptions if file access issues          
def getAttackerInfoPickle(pickleFile):
    try:    
        ATTACKER_INFO = pickle.load(open(pickleFile, "rb"))
        return ATTACKER_INFO
    
    except Exception,e:
        msg = "kojoney_api.py : getAttackerInfoPickle() : exception : " + e.__str__() 
        syslog.syslog(msg)
        print msg
        return False 



if __name__ == "__main__" :
    try:
        ############
        #TEST = True
        #TEST = False
        ############
        
        #ATTACKER_DICT = {}
        
        syslog.openlog("kojoney_api")
        PICKLE_FILE = "/home/var/log/tsom_pickle.dat"
        
        msg = "Started, PICKLE_FILE=" + PICKLE_FILE
        print msg
        syslog.syslog(msg)
        
        while True:
            a = getAttackerInfoPickle(PICKLE_FILE)
            if a == False:
                print "Failed to read ATTACKER_INFO from " + PICKLE_FILE + " , sleeping..."    
                time.sleep(1)
                continue
                
            #print "Read ATTACKER_INFO from " + PICKLE_FILE + " OK"    
            ATTACKER_INFO = a
            #print ATTACKER_INFO.__str__()
            dumpTTYattackerDict(ATTACKER_INFO)
            
            #print "kojoney_api.py : sleeping..."                                                
            time.sleep(30)
            
    except Exception,e:
        msg = "kojoney_api.py : main() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        sys.exit()
   
