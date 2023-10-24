#!/usr/bin/python
import os,time,syslog,sys
#import kojoney_hiddenip
#import ipintellib 
#import twitter_funcs
#import kojoney_blackhole_idmef

ATTACKER_DICT = {}

PHASE_MAX_DURATION = 29 		# 29 secs              -> TESTING
PHASE_MAX_DURATION = 300 		# 300 secs = 5 minutes -> PRODUCTION
                                                                                                                                                                             
def ageAttacks(phaseMaxDuration):
    #global BlackholedRoutes
    global ATTACKER_DICT
    
    try :
        #agedAttackers = []
        agedAttacks = []
        now = time.time()
        #print now
        for attack in ATTACKER_DICT :
            phaseBorn = ATTACKER_DICT[attack]
            phaseAge  = now - phaseBorn
            #print " -> phaseAge for " + attack + " is " + "%.2f" % phaseAge + " secs"
            if phaseAge > phaseMaxDuration :
                #print attack + " has now aged out"
                agedAttacks.append(attack)
                
        for attack in agedAttacks :
            del ATTACKER_DICT[attack] 
            print "[-] attack " + attack + " removed from list of ongoing attacks"
    
    except Exception,e:
        msg = "kojoney_attacker_correlate.py : ageAttack() : exception : " + e.__str__()
        syslog.syslog(msg)
        print msg
        #sys.exit()         
  
# add new attacks to dictionary    
def processAttack(line):
    global ATTACKER_DICT

    try :
        line=line.rstrip("\n")
        
        fields = line.split(",")
        #print fields
        print line
        print " "
        
        attackerIP = fields[3]
        phase      = fields[5]	# SCANNING | ATTACKING etc
        sensor     = fields[7]  # OSSEC
        
        phaseKey   = attackerIP + "-" + phase
        #phaseKey   = attackerIP + "-" + phase + "-" + sensor
        
        if ATTACKER_DICT.has_key(phaseKey) == False :
            print "[+] " + phaseKey + " is a new attack phase, adding to log and DICT of known attacks..."
            ATTACKER_DICT[phaseKey] = time.time()
            fpOut = open("/home/var/log/attacker_correlated.log","a")
            print >> fpOut,line
            fpOut.close()
            print " -> " + line
        else:
            print phaseKey + " is a known attack phase already being monitored, so ignore"
             
    except Exception,e:
        msg = "kojoney_attacker_correlate.py : processAttack() : exception : " + e.__str__()
        syslog.syslog(msg)
        print msg
        sys.exit()         
  

if __name__ == "__main__" :
    try:
        syslog.openlog("kojoney_attacker_correlate")
        msg = "Started, PHASE_MAX_DURATION=" + PHASE_MAX_DURATION.__str__() + " seconds"
        syslog.syslog(msg)
        
        # Tail the uncorrelated Attacker Log
        filenameAttack = '/home/var/log/attacker.log'	# change to csv ?
        fileAttack     = open(filenameAttack,'r')
        print "system     : Open Attacker log file : " + filenameAttack
    
        # Find the size of the Attack file and move to the end
        st_results_attack = os.stat(filenameAttack)
        st_size_attack = st_results_attack[6]
        fileAttack.seek(st_size_attack)
        print "system     : Seek to end of Attacker log file"
    
        while True:
            whereAttack = fileAttack.tell()
            lineAttack  = fileAttack.readline()
            
            if not lineAttack:           # no data
                #print time.ctime() + " Nothing in Attack logfile to process"
                fileAttack.seek(whereAttack)
            else:                       # new data has been added to log file
                print "\n*** NEW EVENT in Attacker Log to process"
                processAttack(lineAttack)
                                                            
            # ageout old attacks
            ageAttacks(PHASE_MAX_DURATION)
        
            #print "sleeping..."
            time.sleep(0.5)
    
    except Exception,e:
        msg = "kojoney_attacker_correlate.py : main() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        sys.exit()
   
