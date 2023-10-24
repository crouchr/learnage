#!/usr/bin/python

# Tail the tweets.log.txt looking fo "URL_FOUND" messages
# if URL is found, then :-
# 1. download it
# 2. run it through clamav
# 3. download all other malware (using wget -r) at that site and analyse that as well
# 4. write results t a file that can be read by kojoney_tweet.py to update Twitter followers of additional info

import time, os , syslog , re 
import syslog
#import ipintellib
import kojoney_idmef_common
import PreludeEasy
import kojoney_attacker_event

#import kojoney_tweet

#from urlparse import urlparse
#import ipintellib	# RCH library - master on mars
#import mailalert	# RCH library
#import p0fcmd		# RCH library - master on mars
#import filter_sebek     # RCH library - master on mars
#import extract_url      # RCH library - master on mars

ROUTER = "172.31.0.9"
HPOT   = "172.31.0.67"
HONEYD = "172.31.0.1"
IBG    = "172.31.0.47"	# IP address sending netflow 

# need this so program can be monitored by monit
# make this a library function
def makePidFile(name):
    pid = os.getpid()
    
    pidFilename = "/var/run/rchpids/" + name + ".pid"
    fp=open(pidFilename,'w')
    print >> fp,pid
    fp.close()            
    #print "pid is " + `pid`
    return pid	# returns None if failed


#
# return the Tweet or None
# Process Ossec alert file
# This is nasty since it is a multi-line file
# This code is now obsolete
def processOssec(line,file):
    
    print "processOssec() : first line read is " + line
    srcIP = "0.0.0.0"
    dstIP = "0.0.0.0"
    user  = "None"
    
    if line.find("** Alert") == -1 :
        print "Ignore additional log details : " + line
        return
        #continue
        
    print "*** Sync  : NEW EVENT in Ossec alerts logfile to process !"
                
    # Header
    #print "first line : " + line
    time.sleep(0.2)
        
    # Log source
    where  = file.tell()
    line2  = file.readline()
    line2  = line2.rstrip('\n')
    #print "line2 = " + line2
    fields = line2.split(" ")
    source = fields[4]
    #print "++ Log source = " + source.__str__()
        
    # Rule number
    # Rule: 5716 (level 5) -> 'SSHD authentication failed.'
    where = file.tell()
    line3  = file.readline()
    line3  = line3.rstrip('\n')
    #print "line3 = " + line3
            
    m = re.findall(r'Rule: (\d+) \(level (\d+)\) -> (.*)',line3)
    if len(m) > 0  :
        #print m.__str__()
        rule = m[0][0]
        #print "++ Rule number = " + rule
        #if m.group(2) != None :
        level = m[0][1]
        print "level=" + level
        if int(level) < 6 :
            print "OSSEC Level is too low, so ignore this Alert, Level=" + level.__str__()
            return
        #print "++ Level = " + level
        #if int(level) >= 5:
            #print "++ Important event, level >= 5" 
        #if m.group(3) != None :
        
        message  = m[0][2]
        message = message.lstrip("'")
        message = message.rstrip("'")
        message = "OSSEC HIDS : " + message 
        #print "++ Message = " + message
        
    # Source IP
    # Src IP: 190.68.110.26
    where  = file.tell()
    line4  = file.readline()
    line4  = line4.rstrip('\n')
    #print "line4 = " + line4
    
    m = re.findall(r'Src IP: (.*)',line4)
    if len(m) > 0  :
        srcIP = m[0]
        #print "++ Source IP = " + srcIP
    else :
         srcIP = "0.0.0.0"   
    attackerIP = srcIP     
        
    # User
    # User: admin
    where  = file.tell()
    line5  = file.readline()
    line5  = line5.rstrip('\n')
    #print "line5 = " + line5
    if "Dst IP" in line:
        m = re.findall(r'Dst IP: (.*)',line5)
        if len(m) > 0  :
            dstIP = m[0]
            print "++ Destination IP = " + dstIP
        else :
             dstIP = "0.0.0.0"   
    #elif "Usr" in line:    
    #    m = re.findall(r'User: (.*)',line5)
    #    if len(m) > 0 :
    #        user = m[0].split(" ")[1]
    #        print "++ User = " + user
    #    else :
    #         user = "err"   
    
    # Log entry
    where  = file.tell()
    line6  = file.readline()
    line6  = line6.rstrip('\n')
    #print "line6 = " + line6
    
    #print "Combined log entry is : " + line + ":" + line2 + ":" + line3 + ":" + line4 + ":" + line5 + ":" + line6
    #print "header     : " + line
    #print "log source : " + line2
    #print "rule       : " + rule
    #print "level      : " + level
    #print "srcIP      : " + srcIP
    #print "dstIP      : " + dstIP
    #print "user       : " + user
    #print "log entry  : " + line6
    #print "========"         
    
    #print "Combined log entry is : " + line + ":" + line2 + ":" + line3 + ":" + line4 + ":" + line5 + ":" + line6
    msg = "srcIP=" + srcIP + " attackerIP=" + attackerIP + " rule=" + rule + " level=" + level + " msg=" + message
    #print msg    
 
 
    client = PreludeEasy.ClientEasy("blackrain")
    client.Start()
             
    # Create the IDMEF message
    idmef = PreludeEasy.IDMEF()
                           
    # Sensor
    fieldsSet = kojoney_idmef_common.setIDMEFcommon(idmef,"Honeypot","02DEBE56",srcIP,dstIP,None,attackerIP,None)
                                            
    # Classification
    idmef.Set("alert.classification.text",message)
                                                  
    # Source
    idmef.Set("alert.source(0).node.address(0).address", srcIP)
    idmef.Set("alert.source(0).service.ip_version", 4)
      
    # Target(s)
    idmef.Set("alert.target(0).node.address(0).address", dstIP)
    idmef.Set("alert.target(0).service.ip_version", 4)
     
    # Additional Data
    fieldsOffset = fieldsSet
    #print "fieldsOffset = " + fieldsOffset.__str__()
    idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
    idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "OSSEC Rule")
    idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", rule)
    
    fieldsOffset = fieldsOffset + 1
    idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
    idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "OSSEC Level")
    idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", level.__str__())
    
    fieldsOffset = fieldsOffset + 1
    idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
    idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "OSSEC Log Source")
    idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", source)
                                                     
    client.SendIDMEF(idmef)
                                                                     
    return None

# Tue Apr 30 07:31:42 2013 Alert Level: 5; Rule: 5716 - SSHD authentication failed.; Location: mars->/var/log/auth.log; srcip: 192.168.1.73; user: crouchr; Apr 30 07:31:38 mars sshd[24396]: Failed password for crouchr from 192.168.1.73 port 52358 ssh2
# Tue Apr 30 07:31:07 2013 Alert Level: 10; Rule: 5720 - Multiple SSHD authentication failures.; Location: mars->/var/adm/auth.log; srcip: 192.168.1.73; user: crouchr; Apr 30 07:31:02 mars sshd[24076]: Failed password for crouchr from 192.168.1.73 port 35568 ssh2
# Wed May  1 06:24:24 2013 Alert Level: 6; Rule: 20101 - IDS event.; Location: mars->/var/adm/syslog; srcip: 200.32.4.10; dstip: 192.168.1.65; May  1 06:24:19 mars snort[2500]: [1:2102003:9] GPL SQL Slammer Worm propagation attempt [Classification: Misc Attack] [Priority: 2]: {UDP} 200.32.4.10:3176 -> 192.168.1.65:1434
def processOssecSyslog(txnId,sensorId,line):
    try:    
        srcIP    = None
        srcPort  = None
        dstIP    = None
        dstPort  = None
        user     = None
        rule     = None
        level    = None
        ruleMsg  = None
        sid      = None
        priority = None
        addInfo1 = None
        addInfo2 = None
        
        line = line.rstrip("\n")        
        #if "IDS" not in line:
        #    return
    
        #print "------------------"
        print line
        
        rule = re.findall("Rule\: (\d+)",line)
        if len(rule) > 0 :
            rule = rule[0]
            #print "OSSEC Rule     : " + rule.__str__()    
    
        if "Rule:" in line :
            ruleMsg = line.split("Rule: " + rule + " - ")[1]
            ruleMsg = ruleMsg.split(";")[0]
            ruleMsg = ruleMsg.rstrip(".")
            #print "OSSEC RuleMsg  : [" + ruleMsg.__str__() + "]"
        
        # level is a <str>        
        level = re.findall("Alert Level\: (\d+)",line)
        if len(level) > 0 :
            level = level[0]
            #print "OSSEC Level    : " + level    
            addInfo1 = "LEVEL=" + level.__str__()
        
        if "Location:" in line :
            location = line.split("Location: ")[1]
            location = location.split(";")[0]
            #print "OSSEC Location : [" + location.__str__() + "]"
    
        if "user:" in line :
            user = line.split("user: ")[1]
            user = user.split(";")[0]
            #print "OSSEC User     : [" + user.__str__() + "]"
    
        if "srcip:" in line :
            ips = re.findall("srcip\: (\d+\.\d+\.\d+\.\d+)",line)
            if len(ips) > 0 :
                srcIP = ips[0]
                #print "OSSEC srcIP    : " + srcIP.__str__()
    
        if "dstip:" in line :
            ips = re.findall("dstip\: (\d+\.\d+\.\d+\.\d+)",line)
            if len(ips) > 0 :
                dstIP = ips[0]
                #print "OSSEC dstIP    : " + dstIP.__str__()
    
        # -------- SPECIFIC RULES ----------        
        if ("IDS event" in ruleMsg or "First time this IDS alert is generated" in ruleMsg):
        # and ("{UDP}" in line or "{TCP}" in line) :
            #print "Snort-specific decoding"
            if ("{TCP}" in line or "{UDP}" in line):
                ips = re.findall("(\d+\.\d+\.\d+\.\d+)\:(\d+) -> (\d+\.\d+\.\d+\.\d+)\:(\d+)",line)
                #print ips.__str__()
                srcPort = ips[0][1]
                dstPort = ips[0][3]
                 
            #elif ("{TCP}" in line or "{UDP}" in line):
            #    ips = re.findall("(\d+\.\d+\.\d+\.\d+)\:(\d+) -> (\d+\.\d+\.\d+\.\d+)\:(\d+)",line)
            #    #print ips.__str__()
            #    srcPort = ips[0][1]
            #    dstPort = ips[0][3]
            
            sid = re.findall("\[(\d+)\:(\d+)\:\d+\]",line)
            if len(sid) > 0:
                #print "IDS sid=" + sid.__str__()
                sid = sid[0][0] + ":" + sid[0][1]
                msg = "kojoney_ossec_parse.py : parsed Snort SID " + sid.__str__() + " from " + line
                #addInfo1 = sid.__str__()
                #print msg
            
            # Snort Message
            snortMsg = line.replace("]: ","")    
            snortMsg = snortMsg.split(']')[1]
            snortMsg = snortMsg.split('[')[0]
            snortMsg = snortMsg.lstrip(" ")    
            snortMsg = snortMsg.rstrip(" ")    
            #print "snortMsg=(" + snortMsg + ")"  
            
            # Classification - this is not in every Snort message
            if "Classification" in line:
                classification = line.split("Classification: ")[1]
                classification = classification.split("]")[0]
                classification = classification.replace(" ","_")
                classification = classification.upper()
            else:
                classification = "UNCLASSIFIED"
            #print "classification=(" + classification + ")"  
                        
            priority = re.findall("Priority\: (\d+)",line)
            if len(priority) > 0 :
                priority = priority[0]
                msg = "kojoney_ossec_parse.py : Snort Priority=" + priority
                addInfo2 = snortMsg + ":" + "PRI=" + priority.__str__() + ":" + "CL=" + classification + ":" + "SID=" + sid.__str__()
                #print msg
                              
        # Update Attacker Database
        #print "kojoney_ossec_parse : priority=" + priority.__str__()
        
        if (priority != None and int(priority) == 1) or "ATTACK" in line.upper() :	# Snort
            kojoney_attacker_event.generateAttackerEvent(txnId,srcIP,None,sensorId,"ATTACKING"     ,"OSSEC",rule,ruleMsg,None,None,None,addInfo1,addInfo2)
        elif priority != None and int(priority) == 2 :					# Snort
            kojoney_attacker_event.generateAttackerEvent(txnId,srcIP,None,sensorId,"SCANNING"      ,"OSSEC",rule,ruleMsg,None,None,None,addInfo1,addInfo2)
        elif priority != None and int(priority) == 3 :					# Snort
            kojoney_attacker_event.generateAttackerEvent(txnId,srcIP,None,sensorId,"PROBING"       ,"OSSEC",rule,ruleMsg,None,None,None,addInfo1,addInfo2)
        elif int(level) < 12 :
            #print "OSSEC : generic classification"
            kojoney_attacker_event.generateAttackerEvent(txnId,srcIP,None,sensorId,"ATTACKING"     ,"OSSEC",rule,ruleMsg,None,None,None,addInfo1,addInfo2)
        else :
            kojoney_attacker_event.generateAttackerEvent(txnId,srcIP,None,sensorId,"GAINED_ACCESS" ,"OSSEC",rule,ruleMsg,None,None,None,addInfo1,addInfo2)
                 
                            
        # ---------- IDMEF ----------
        attackerIP = srcIP
        #print "Combined log entry is : " + line + ":" + line2 + ":" + line3 + ":" + line4 + ":" + line5 + ":" + line6
        #msg = "srcIP=" + srcIP + " attackerIP=" + attackerIP + " rule=" + rule + " level=" + level + " msg=" + message
        #print msg    
 
        client = PreludeEasy.ClientEasy("blackrain")
        client.Start()
             
        # Create the IDMEF message
        idmef = PreludeEasy.IDMEF()
                           
        # Sensor
        fieldsSet = kojoney_idmef_common.setIDMEFcommon(idmef,"Honeypot",sensorId,srcIP,dstIP,None,attackerIP,line)
                                            
        # Classification
        idmef.Set("alert.classification.ident",rule)	# ident = OSSEC Rule
        
        text = "OSSEC " + rule + " : " + ruleMsg 
        if sid != None:
            text = text + " [" + sid.__str__() + "]"
        #print text    
        idmef.Set("alert.classification.text",text)
                                                  
        # Source
        if srcIP != None:
            idmef.Set("alert.source(0).node.address(0).address", srcIP)
            idmef.Set("alert.source(0).service.ip_version", 4)
    
        if srcPort != None:
            idmef.Set("alert.source(0).service.port", dstPort)
      
        # Target(s)
        if dstIP != None:
            idmef.Set("alert.target(0).node.address(0).address", dstIP)
            idmef.Set("alert.target(0).service.ip_version", 4)
    
        if dstPort != None:
            idmef.Set("alert.target(0).service.port", dstPort)
    
        # Targetted User
        if user != None:
            idmef.Set("alert.target(0).user.category","application")
            idmef.Set("alert.target(0).user.user_id(0).type","target-user")
            idmef.Set("alert.target(0).user.user_id(0).name",user)
                     
        # Severity is based on OSSEC Level
        if int(level) >= 12 :
            severity = "high"
        elif int(level) >= 7 and int(level) < 12 :
            severity = "medium" 
        else :
            severity = "low"
        #print "severity : " + severity    
        idmef.Set("alert.assessment.impact.severity", severity) 
        
        #idmef.Set("alert.source(0).process.name","OSSEC")
                             
        # Additional Data
        fieldsOffset = fieldsSet
        #print "fieldsOffset = " + fieldsOffset.__str__()
        #idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        #idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "OSSEC Rule")
        #idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", rule)
    
        #fieldsOffset = fieldsOffset + 1
        msg = "Level " + level
        #print msg
        #idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "OSSEC Level")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", msg)
    
        fieldsOffset = fieldsOffset + 1
        #idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "OSSEC Log Location")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", location)
                                                     
        client.SendIDMEF(idmef)
                                                                     
        return None
        
    except Exception,e:
        msg = "processOssecSyslog() : exception : " + e.__str__() + " line=" + line + "]"
        print msg
        syslog.syslog(msg)

# Write to a test file events to be Tweeted
def writeImportantKojOssecFile(msg): 
    print "kojoney_ossec_parse.py : *** IMPORTANT Ossec event *** :-"
    print getTimestamp(),msg
    
    fp=open('/home/var/log/kojoney_ossec.log','a')
    print >> fp,getTimestamp(),msg
    fp.close()            
    
    return msg	
    

def getTimestamp():
    now = time.time()
    nowLocal = time.gmtime(now)
    return time.asctime(nowLocal)
                               
# -------------------------------------------------------
        
# Start of code        
        
if __name__ == '__main__' :
       
# Make pidfile so we can be monitored by monit        
    pid =  makePidFile("test_ossec")
    if pid == None:
        syslog.syslog("Failed to create pidfile for pid " + `pid`)
        sys.exit(0)
    else:
        syslog.syslog("kojoney_ossec_parse.py started with pid " + `pid`)
                
    # Send an email to say kojoney_tail has started
    now = time.time()
    nowLocal = time.gmtime(now)
    #makeMsg(0,"0","system,kojoney_viz started with pid=" + `pid` + " at localtime " + time.asctime(nowLocal))
    a = "kojoney_ossec_parse.py started with pid=" + `pid`

    #statusAlert("*** kojoney_tweet started ***",a)

    # Set the Tweets los filename to scan
    filename = '/var/ossec/logs/alerts/alerts.log'
    filename = '/home/var/log/ossec.log'
    file = open(filename,'r')

# ------------
# tail -f mode
# ------------

# Find the size of the file and move to the end
#    st_results = os.stat(filename)
#    st_size = st_results[6]
#    file.seek(st_size)

    print "system     : Seek to end of Ossec alerts log feed " + filename

    while True:
    
        # Tweets log file       
        #where = file.tell()
        line  = file.readline()
        line  = line.rstrip('\n')
        
        if not line:		# no data to process
            #print "nothing in Ossec alerts logfile to process"
            #file.seek(where)
            pass
        else :			# new data has been added to ossec log file
            #print line
            
            if "IDS event" in line:
            #if "integrity" in line.lower():
                processOssecSyslog(111,"TEST",line)
        
        #print "sleeping..."
        # this can be a float for sub-second sleep    
        time.sleep(0.1)	
                              
                                          