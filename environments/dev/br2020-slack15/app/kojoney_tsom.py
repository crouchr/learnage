#!/usr/bin/python
import os,time,syslog,sys
import ipintellib 
import operator
import pickle 		# shelve does not work with bb_freeze

#ATTACKER_DICT = {}
#ATTACKER_INFO = {}                                                                                                                                                                             

WEIGHT = { 'PROBING' : 1 ,  'SCANNING'  : 3 ,        'PSCAN' : 4 ,\
            'BHOLE'  : 5 ,  'ATTACKING' : 15 ,       'GAINED_ACCESS' : 30 ,\
            'MWARE'  : 30 , 'MAINTAIN_ACCESS' : 40 , 'COVER_TRACKS' : 50 , 'HUMAN_ACTIVITY' : 80 }

# Return a string with flags in correct sequence order
# Note : Not all flag may be present in the flags string 
def orderFlags(flags):
    try:
        WEIGHTLIST = ['PR','SC','PS','BH','AT','GA','MW','MA','CO','HU']
        #print "entered orderFlags()"
        #print "IN [" + flags + "]"
        flags    = flags.rstrip(" ")
        flagList = flags.split(" ")
        #print "flagList = " + flagList.__str__()
        orderedList = []
        
        for phaseShort in WEIGHTLIST:
            #print phaseShort
            if phaseShort in flagList:
                orderedList.append(phaseShort) 
        #myorder = [0,1,2,3,4,5,6,7,8,9]
        #orderedList = [ flagList[i] for i in myorder]
        #print orderedList
        orderedString = " ".join(orderedList) + " "
        #print "OUT [" + orderedString + "]"
    
        return orderedString         
    
    except Exception,e:
        msg = "kojoney_tsom.py : orderFlags() : exception : " + e.__str__() 
        syslog.syslog(msg)
        print msg
        return None 

  
# add new attacks to dictionary    
def process(line,ATTACKER_DICT,ATTACKER_INFO,lifetimeID):
    #global ATTACKER_DICT
    #global ATTACKER_INFO
    attack = {}		# one single attack
    attackerInfo = {}
    attackList   = []
     
    try :
        line = line.rstrip("\n")
        #print "---------"
        fields = line.split(",")
        #print fields
        #print line
        #print " "
        epoch      = fields[1]        
        tstamp     = fields[2]
        attackerIP = fields[3]
        phase      = fields[5]	# SCANNING | ATTACKING etc
        osShort    = fields[6]
        sensor     = fields[7]  # OSSEC
        sensorMsg  = fields[9]
        addInfo1   = fields[13]
        addInfo2   = fields[14]
        
        #print tstamp
        #print attackerIP
        #print phase
        #print "osShort=" + osShort
        
        #phaseKey   = attackerIP + "-" + phase
        #phaseKey   = attackerIP + "-" + phase + "-" + sensor
        
        if ATTACKER_DICT.has_key(attackerIP) == False :
            print "[+] kojoney_tsom : process() : " + time.ctime() + " " + lifetimeID + " " + attackerIP + " has NOT been seen before, so create a new attacker record..."
            attack['epoch']     = epoch
            attack['tstamp']    = tstamp
            attack['phase']     = phase
            attack['sensor']    = sensor
            attack['sensorMsg'] = sensorMsg
            attack['addInfo1']  = addInfo1
            attack['addInfo2']  = addInfo2
            attackList.append(attack)
            
            # Data enhancement
            # ----------------
            # GeoIP
            geoIP = ipintellib.geo_ip(attackerIP)
            attackerInfo['cc']   = geoIP['countryCode']
            attackerInfo['city'] = geoIP['city']         
            attackerInfo['latitude']  = geoIP['latitude']         
            attackerInfo['longitude'] = geoIP['longitude']         
            
            # p0f
            attackerInfo['os'] = osShort         
            
            # IP record creation time
            attackerInfo['epoch'] = epoch         

            # phases the attacker has tried
            attackerInfo['flags'] = ""
                        
            # Peak value of CTL
            attackerInfo['ctlPeak']    = 0.0
            attackerInfo['ctlSumPeak'] = 0.0

            # store details of the last attack            
            attackerInfo['lastSensor']         = sensor
            attackerInfo['lastSensorMsg']      = sensorMsg
            attackerInfo['lastSensorTime']     = time.ctime()
            attackerInfo['lastSensorAddInfo1'] = addInfo1
            attackerInfo['lastSensorAddInfo2'] = addInfo2
          
            # DNS info
            dnsInfo = ipintellib.ip2name(attackerIP)
            attackerInfo['rdns'] = dnsInfo['name'].rstrip('.')                   	# right-strip the trailing .
                                    
            # WHOIS - AS number        
            asInfo = ipintellib.ip2asn(attackerIP)                                
            if asInfo['as'] == "AS-none" :
                as = "Unknown"
            else:
                as = "AS" + asInfo['as']    
            attackerInfo['as']  = as			                       	# AS123   
            
            # WHOIS - ISP name
            if asInfo['registeredCode'] == "whois-failed" :
                isp = "Unknown"
            else:
                isp = asInfo['registeredCode']        
            attackerInfo['isp'] = isp					# Short-form e.g.ARCOR
                                                                    
            #print attackerInfo.__str__()
            #print attack.__str__()
            ATTACKER_DICT[attackerIP] = attackList
            ATTACKER_INFO[attackerIP] = attackerInfo
            #print ATTACKER_DICT.__str__() 
            #ATTACKER_DICT[phaseKey] = time.time()
            
            #print " -> " + line
        else:
            print "[+] kojoney_tsom : process() : " + lifetimeID + " " + attackerIP + " has been seen before so append attack to existing list of attacks"
            attack['epoch']     = epoch
            attack['tstamp']    = tstamp
            attack['phase']     = phase
            attack['sensor']    = sensor
            attack['sensorMsg'] = sensorMsg
            attack['addInfo1']  = addInfo1
            attack['addInfo2']  = addInfo2
            
            #print attack.__str__()
            ATTACKER_DICT[attackerIP].append(attack)
            #print ATTACKER_DICT.__str__()
            
            # p0f - update if os is not already set
            attackerInfo = ATTACKER_INFO[attackerIP]
            if osShort != "none" and attackerInfo['os'] == "none" :
                print "kojoney_tsom : " + time.ctime() + " " + lifetimeID + " " + "New information received, so update attacker OS info"
                attackerInfo['os'] = osShort
                ATTACKER_INFO[attackerIP]  = attackerInfo         
            
            # store details of the last attack            
            attackerInfo = ATTACKER_INFO[attackerIP]
            attackerInfo['lastSensor']         = sensor
            attackerInfo['lastSensorMsg']      = sensorMsg
            attackerInfo['lastSensorTime']     = time.ctime()
            attackerInfo['lastSensorAddInfo1'] = addInfo1
            attackerInfo['lastSensorAddInfo2'] = addInfo2
            ATTACKER_INFO[attackerIP]  = attackerInfo         
            
    except Exception,e:
        msg = "kojoney_tsom.py : process() : exception : " + e.__str__() + " for lifetimeID=" + lifetimeID
        syslog.syslog(msg)
        print msg
        return 
        
# Calculate and update CTL values
def calcCTL(ATTACKER_DICT_P1,ATTACKER_INFO_P1,ATTACKER_DICT_P2,ATTACKER_INFO_P2):
    try:
        
        # first two characters are the values use for the attack phase flags
        global WEIGHT
        # = { 'PROBING' : 1 , 'SCANNING' : 3 , 'PSCAN' : 4 , 'BHOLE' : 5 , 'ATTACKING' : 15 , 'GAINED_ACCESS' : 30 , 'MWARE' : 30 , 'MAINTAIN_ACCESS' : 40 , 'COVER_TRACKS' : 50 , 'HUMAN_ACTIVITY' : 80 }
        
        # P1
        # --
        if len(ATTACKER_DICT_P1) > 0 :
            #print "P1 lifetime"
            #print "-----------" 
            for ip in ATTACKER_DICT_P1 :
                flags = ATTACKER_INFO_P1[ip]['flags']
                attackerWeight = 0 
                attackerEvents = 0   
                attackList = ATTACKER_DICT_P1[ip]
                for attack in attackList:
                    attackerEvents = attackerEvents + 1
                    attackerWeight = attackerWeight + WEIGHT[attack['phase']]
                    phaseShort = attack['phase'][0:2].upper()	# first two characters
                    if phaseShort not in flags:
                        flags = flags + phaseShort + " "
                
                ATTACKER_INFO_P1[ip]['flags'] = flags
                ATTACKER_INFO_P1[ip]['ctl'] = float(attackerWeight) / float(attackerEvents)
                ATTACKER_INFO_P1[ip]['eventsSum'] = attackerEvents
                ATTACKER_INFO_P1[ip]['weightSum'] = attackerWeight 
                ATTACKER_INFO_P1[ip]['ctlSum'] = 0.0		# Just set to a dummy value to be overidden by the P2 calculation
                
                if ATTACKER_INFO_P1[ip]['ctl'] > ATTACKER_INFO_P1[ip]['ctlPeak']:
                    ATTACKER_INFO_P1[ip]['ctlPeak'] = ATTACKER_INFO_P1[ip]['ctl'] 
                    print ip + " has new P1 ctlPeak=" + "%.1f" % ATTACKER_INFO_P1[ip]['ctlPeak']
                
                #print "calcCTL() : P1 weightSum for " + ip + " is %.1f" % ATTACKER_INFO_P1[ip]['weightSum'] 
                #print "calcCTL() : P1 eventsSum for " + ip + " is %.1f" % ATTACKER_INFO_P1[ip]['eventsSum'] 
                #print "calcCTL() : P1       CTL for " + ip + " is %.1f" % ATTACKER_INFO_P1[ip]['ctl']
                ##print "calcCTL() : P1 Total CTL for " + ip + " is %.1f" % ATTACKER_INFO_P1[ip]['ctlSum']
                #print " "
        # P2
        # --
        if len(ATTACKER_DICT_P2) > 0 : 
            #print "P2 lifetime"
            #print "-----------" 
            for ip in ATTACKER_DICT_P2 :
                flags = ATTACKER_INFO_P2[ip]['flags']
                attackerWeight = 0 
                attackerEvents = 0   
                attackList = ATTACKER_DICT_P2[ip]
                for attack in attackList:
                    attackerEvents = attackerEvents + 1
                    attackerWeight = attackerWeight + WEIGHT[attack['phase']]
                    phaseShort = attack['phase'][0:2].upper()	# first two characters
                    if phaseShort not in flags:
                        flags = flags + phaseShort + " "
                
                ATTACKER_INFO_P2[ip]['flags'] = flags
                ATTACKER_INFO_P2[ip]['eventsSum'] = attackerEvents
                ATTACKER_INFO_P2[ip]['weightSum'] = attackerWeight 
                
                ATTACKER_INFO_P2[ip]['ctl']    = float(attackerWeight) / float(attackerEvents)
                
                # ctlSum = CTL for P1 + CTL for P2
                if ATTACKER_INFO_P1.has_key(ip) :
                    ATTACKER_INFO_P2[ip]['ctlSum'] = float(ATTACKER_INFO_P2[ip]['ctl']) + float(ATTACKER_INFO_P1[ip]['ctl'])
                    ATTACKER_INFO_P1[ip]['ctlSum'] = float(ATTACKER_INFO_P2[ip]['ctl']) + float(ATTACKER_INFO_P1[ip]['ctl'])
                else:
                    ATTACKER_INFO_P2[ip]['ctlSum'] = float(ATTACKER_INFO_P2[ip]['ctl'])  
                
                if ATTACKER_INFO_P2[ip]['ctl'] > ATTACKER_INFO_P2[ip]['ctlPeak']:
                    ATTACKER_INFO_P2[ip]['ctlPeak'] = ATTACKER_INFO_P2[ip]['ctl'] 
                    print ip + " has new P2 ctlPeak=" + "%.1f" % ATTACKER_INFO_P2[ip]['ctlPeak']
                
                if ATTACKER_INFO_P2[ip]['ctlSum'] > ATTACKER_INFO_P2[ip]['ctlSumPeak']:
                    ATTACKER_INFO_P2[ip]['ctlSumPeak'] = ATTACKER_INFO_P2[ip]['ctlSum'] 
                    print ip + " has new ctlSumPeak=" + "%.1f" % ATTACKER_INFO_P2[ip]['ctlSumPeak']
                
                #print "calcCTL() : P2 weightSum for " + ip + " is %.1f" % ATTACKER_INFO_P2[ip]['weightSum'] 
                #print "calcCTL() : P2 eventsSum for " + ip + " is %.1f" % ATTACKER_INFO_P2[ip]['eventsSum'] 
                #print "calcCTL() : P2       CTL for " + ip + " is %.1f" % ATTACKER_INFO_P2[ip]['ctl']
                #print "calcCTL() : P2 Total CTL for " + ip + " is %.1f" % ATTACKER_INFO_P2[ip]['ctlSum']
                #print " "
                         
    except Exception,e:
        msg = "kojoney_tsom.py : calcCTL() : exception : " + e.__str__() 
        syslog.syslog(msg)
        print msg
        return  

# dump current state of attackers/attacks to a file for monitoring / debugging
def dumpFileAttackerDict(ATTACKER_DICT,ATTACKER_INFO,filename,lifetimeID):
    try:
        
        if len(ATTACKER_INFO) <= 0 :
            print "dumpAttackerDict() : No attackers to dump information for, so early return for lifetimeID=" + lifetimeID
            return
            
        fpOut = open(filename,'w')
        print >> fpOut," "
        print >> fpOut,"attackerCache for " + lifetimeID
        print >> fpOut,"--------------------"
        print >> fpOut,"Last updated : " + time.ctime()
        print >> fpOut," " 
        for ip in ATTACKER_DICT:
            #attackerWeight = 0 
            #attackerEvents = 0   
            print >> fpOut," "
            print >> fpOut,"ATTACKER : " + ip + " " + "[" + ATTACKER_INFO[ip]['rdns'] + "]" + " " + "OS=" + ATTACKER_INFO[ip]['os'] + " " + "(" + ATTACKER_INFO[ip]['city'] + "," + ATTACKER_INFO[ip]['cc'] + ")" + " " + "%.2f" % ATTACKER_INFO[ip]['latitude'] + "N " + "%.2f" % ATTACKER_INFO[ip]['longitude'] + "E"
            print >> fpOut," Network : " + "AS" + ATTACKER_INFO[ip]['as'] + " " + ATTACKER_INFO[ip]['isp'] 
            
            attackList = ATTACKER_DICT[ip]
            for attack in attackList:
                #attackerEvents = attackerEvents + 1
                #attackerWeight = attackerWeight + WEIGHT[attack['phase']]
                #ATTACKER_INFO[ip]['ctl'] = float(attackerWeight) / float(attackerEvents)
                print >> fpOut," "
                print >> fpOut," " + attack['tstamp'].__str__() + " " + attack['phase'] + " : " + attack['sensor'] + " => " + attack['sensorMsg']
                print >> fpOut,"  " + attack['addInfo1'] + " " + attack['addInfo2']  
            print >> fpOut, " "
            #print >> fpOut, "attackerWeight=" + attackerWeight.__str__() + " attackerEvents=" + attackerEvents.__str__()
            print >> fpOut, "=> " + lifetimeID + " : Attacker Compound Threat Level (CTL) : %.1f" % ATTACKER_INFO[ip]['ctl']
            
        print >> fpOut," "
        print >> fpOut,"-------------"
        print >> fpOut," "
        fpOut.close()
                    
    except Exception,e:
        msg = "kojoney_tsom.py : dumpFileAttackerDict() : exception : " + e.__str__() + " for lifetimeID=" + lifetimeID
        syslog.syslog(msg)
        print msg
        return  

# dump current state of attackers/attacks to TTY in descending order of CTL
# This is only for debug - the master is in kojoney_api.py
def dumpTTYattackerDict(ATTACKER_DICT,ATTACKER_INFO):
    try:
        
        X = {}
        
        if len(ATTACKER_INFO) <= 0 :
            print "dumpTTYattackerDict() : No attackers to dump information for, so early return"
            return
            
        for ip in ATTACKER_DICT:
            #print "RT : " + ip + " (" + ATTACKER_INFO[ip]['rdns'] + ")" + " CTL=%.1f" % ATTACKER_INFO[ip]['ctlSum'] + " " + ATTACKER_INFO[ip]['os'] + " (" + ATTACKER_INFO[ip]['cc'] + "," + ATTACKER_INFO[ip]['city'] + ")" + " %.2fN" % ATTACKER_INFO[ip]['latitude'] + " %.2fE" % ATTACKER_INFO[ip]['longitude'] + " " + ATTACKER_INFO[ip]['as'] + " " + ATTACKER_INFO[ip]['isp'] + " (P2 #W=" + ATTACKER_INFO[ip]['weightSum'].__str__() + " P2 #E=" + ATTACKER_INFO[ip]['eventsSum'].__str__() +")" 
            X[ip] = ATTACKER_INFO[ip]['ctlSum']
        
        #print "Unsorted : " + X.__str__()    
        
        # Sort based on ctl value, highest at head of list
        SORTED_LIST = sorted(X.iteritems(), key = operator.itemgetter(1), reverse=True)
        #print "Sorted   : " + SORTED_LIST.__str__()    
        
        # Display in order of CTL (descending)
        for a in SORTED_LIST:
            ip = a[0] 
            print "RT : " + ip + " (" + ATTACKER_INFO[ip]['rdns'] + ")" + " CTL=%.1f" % ATTACKER_INFO[ip]['ctlSum'] + " {%.1f}" % ATTACKER_INFO[ip]['ctlPeak'] + " " + ATTACKER_INFO[ip]['os'] + " (" + ATTACKER_INFO[ip]['cc'] + "," + ATTACKER_INFO[ip]['city'] + ")" + " %.2fN" % ATTACKER_INFO[ip]['latitude'] + " %.2fE" % ATTACKER_INFO[ip]['longitude'] + " " + ATTACKER_INFO[ip]['as'] + " " + ATTACKER_INFO[ip]['isp'] + " (P2 #W=" + ATTACKER_INFO[ip]['weightSum'].__str__() + " P2 #E=" + ATTACKER_INFO[ip]['eventsSum'].__str__() +")" 
            print "  flags=" + ATTACKER_INFO[ip]['flags'].rstrip(" ")            

    except Exception,e:
        msg = "kojoney_tsom.py : dumpTTYattackerDict() : exception : " + e.__str__() 
        syslog.syslog(msg)
        print msg
        return  

# Pickle the Attacker Info database to file so that other programs can use it
def pickleAttackerInfo(ATTACKER_INFO):
    try:
        PICKLE_FILE = "/home/var/log/tsom_pickle.dat"
        pickle.dump(ATTACKER_INFO, open(PICKLE_FILE,"wb"))
        #print "pickleAttackerInfo() : pickled ATTACKER_INFO to " + PICKLE_FILE
        
    except Exception,e:
        msg = "kojoney_tsom.py : pickleAttackerInfo() : exception : " + e.__str__() 
        syslog.syslog(msg)
        print msg
        return  

        
# lifetime is in seconds
# Prune out expired attacks and attackers
def pruneAttackerDict(ATTACKER_DICT,ATTACKER_INFO,lifetime,test,lifetimeID):
    try:
        #global ATTACKER_DICT
        #global ATTACKER_INFO
        
        #print "pruneAttackerDict() called"
        
        ipRemoveList = []
        now = time.time()
        
        for ip in ATTACKER_DICT:
            #print "Attacker : " + ip		# nominal comfort during debugging
            attackList = ATTACKER_DICT[ip]
            for attack in attackList:
                epoch = attack['epoch']
                #print "  epoch : " + epoch.__str__()
                if float(now) - float(epoch) >= float(lifetime):
                    print "[-] kojoney_tsom : " + lifetimeID + " attack record has exceeded lifetime, so DELETE attack=" + attack.__str__()
                    attackList.remove(attack)  
                    ATTACKER_DICT[ip] = attackList
                    if len(attackList) == 0 :
                        print "[-] kojoney_tsom : " + lifetimeID + " attackList for attacker " + ip + " is now empty, so mark for deletion"
                        #del ATTACKER_DICT[ip]
                        ipRemoveList.append(ip)
        
        # Purge the aged out attacker IPs  
        for ip in ipRemoveList:
            dumpTSOMrec(ip,ATTACKER_INFO[ip],test,lifetimeID)
            
            print "pruneAttackerDict() : " + lifetimeID + " : DELETE ATTACKER_DICT[] for " + ip + " " + ATTACKER_DICT[ip].__str__()
            del ATTACKER_DICT[ip]
            
            print "pruneAttackerDict() : " + lifetimeID + " : DELETE ATTACKER_INFO[] for  " + ip + " " + ATTACKER_INFO[ip].__str__()
            del ATTACKER_INFO[ip]
                            
    except Exception,e:
        msg = "kojoney_tsom.py : pruneAttackerDict() : exception : " + e.__str__() + " for lifetimeID=" + lifetimeID
        syslog.syslog(msg)
        print msg
        return  
        
# This file is also tailed by kojoney_tweet and is used when ctl changes
# This data should be written to a SQL database for long-term statistics
def dumpTSOMrec(ip,attackerInfo,test,lifetimeID):
    try:
        #print "dumpTSMOrec() called"
        
        deleteEpoch = time.time()
        ipLifetime = deleteEpoch - float(attackerInfo['epoch'])		# now - time that the IP was first seen attacking
        
        if lifetimeID == "P1" :
            CTL = attackerInfo['ctlPeak']
        else:
            CTL = attackerInfo['ctlSumPeak']
        flags = attackerInfo['flags'].rstrip(" ")
              
        #msg = "tstamp=" + time.ctime() + ", ip=" + ip + ", " + lifetimeID + "CTLpeak=" + "%.1f" % CTL + ", createEpoch=" + "%.2f" % float(attackerInfo['epoch']) + ", pruneEpoch=" + "%.2f" % deleteEpoch + ", cc=" + attackerInfo['cc'] + ", city=" + attackerInfo['city'] + ", rdns=" + attackerInfo['rdns'] + ", net=" + "AS" + attackerInfo['as'] + ", isp=" + attackerInfo['isp'] + ", os=" + attackerInfo['os'] + ", lifetimeSecs=" + "%.1f" % ipLifetime  
        msg = "tstamp=" + time.ctime() + ", ip=" + ip + ", cc=" + attackerInfo['cc'] + ", flags=" + '"' + flags + '"' + ", " + lifetimeID + "CTLpeak=" + "%.1f" % CTL +  ", city=" + '"' + attackerInfo['city'] + '"' + ", rdns=" + attackerInfo['rdns'] + ", net=" + attackerInfo['as'] + ", isp=" + '"' + attackerInfo['isp'] + '"' + ", os=" + attackerInfo['os'] + ", createEpoch=" + time.ctime(float(attackerInfo['epoch'])) + ", pruneEpoch=" + time.ctime(deleteEpoch) + ", lifetimeSecs=" + "%.1f" % ipLifetime  
        
        print "**** " + lifetimeID + " dumpTSOMrec() : " + msg
        
        if test == True :
           filename = "/home/var/log/tsom_dump_test.csv"
        else:
           filename = '/home/var/log/tsom_dump.csv'
        
        fpOut = open(filename,'a')
        print >> fpOut,msg
        fpOut.close()
         
    except Exception,e:
        msg = "kojoney_tsom.py : dumpTSOMrec() : exception : " + e.__str__() + " for lifetimeID=" + lifetimeID
        syslog.syslog(msg)
        print msg
        return 


if __name__ == "__main__" :
    try:
        ############
        #TEST = True
        TEST = False
        ############
        
        ATTACKER_DICT_P1 = {}
        ATTACKER_INFO_P1 = {}                                                                                                                                                                             
        
        ATTACKER_DICT_P2 = {}
        ATTACKER_INFO_P2 = {}                                                                                                                                                                             
        
        if TEST == True :
            P1 = 60			# 20 seconds = TEST
            P2 = 120			# 60
            filenameAttack = '/home/var/log/attacker.log'			
        else:
            P1 = 300			# 5 minutes  = PRODUCTION
            P2 = 7200			# 7200 = 2 hours
            filenameAttack = '/home/var/log/attacker_correlated.log'	
        
        ATTACKER_CACHE_FILE_P1 = '/home/var/log/attackerCacheP1.txt'
        ATTACKER_CACHE_FILE_P2 = '/home/var/log/attackerCacheP2.txt'
        
        syslog.openlog("kojoney_tsom")
        msg = "Started, TEST=" + TEST.__str__() + " P1=" + P1.__str__() + " seconds, P2=" + P2.__str__() + " seconds, attackerCacheFileP1=" + ATTACKER_CACHE_FILE_P1 + ", attackerCacheFileP2=" + ATTACKER_CACHE_FILE_P2
        print msg
        syslog.syslog(msg)
        cycle = 0
        
        fileAttack     = open(filenameAttack,'r')
        print "system     : Open Attacker Log file : " + filenameAttack
    
        # Find the size of the Attack file and move to the end
        st_results_attack = os.stat(filenameAttack)
        st_size_attack = st_results_attack[6]
        fileAttack.seek(st_size_attack)
        print "system     : Seek to end of Attacker Log file"
    
        while True:
            whereAttack = fileAttack.tell()
            lineAttack  = fileAttack.readline()
            
            if not lineAttack:           # no data
                #print time.ctime() + " Nothing in Attack logfile to process"
                fileAttack.seek(whereAttack)
            else:                       # new data has been added to log file
                print "\n*** NEW EVENT in Attacker (Correlated) Log to process"
                print lineAttack
                process(lineAttack,ATTACKER_DICT_P1,ATTACKER_INFO_P1,"P1")
                process(lineAttack,ATTACKER_DICT_P2,ATTACKER_INFO_P2,"P2")
            
            #print "sleeping..."                                                
            #time.sleep(1)
            
            # Update data about the attackers / attacks etc.
            cycle = cycle + 1
            if cycle >= 50 :	# every 10 seconds approx
                print "\nkojoney_tsom : Updating Threat Level calculations..."
                # Calc individual CTL for each phase P1 and P2 and P1 + P2"
                calcCTL(ATTACKER_DICT_P1,ATTACKER_INFO_P1,ATTACKER_DICT_P2,ATTACKER_INFO_P2)
                
                # Dump info to file phase"
                dumpFileAttackerDict(ATTACKER_DICT_P1,ATTACKER_INFO_P1,ATTACKER_CACHE_FILE_P1,"P1")
                dumpFileAttackerDict(ATTACKER_DICT_P2,ATTACKER_INFO_P2,ATTACKER_CACHE_FILE_P2,"P2")
                
                # optional : Dump to TTY"
                #dumpTTYattackerDict(ATTACKER_DICT_P2,ATTACKER_INFO_P2)
                
                # Write attacker info to file that can be read by remote access processes
                pickleAttackerInfo(ATTACKER_INFO_P2)
                
                # Prune database phase"
                pruneAttackerDict(ATTACKER_DICT_P1,ATTACKER_INFO_P1,P1,TEST,"P1")
                pruneAttackerDict(ATTACKER_DICT_P2,ATTACKER_INFO_P2,P2,TEST,"P2") 
                        
                cycle = 0
            
            #print "sleeping..."                                                
            time.sleep(0.5)
                        
    except Exception,e:
        msg = "kojoney_tsom.py : main() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        sys.exit()
   
