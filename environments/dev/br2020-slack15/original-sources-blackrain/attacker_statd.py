#!/usr/bin/python

# Parse the Netflow file in order to update attacker statistics

import time, os , syslog 
import re
import glob
import ipintellib
import kojoney_hiddenip

import shelve

honeypotIPs = ["192.168.1.50","192.168.1.60","192.168.1.61","192.168.1.62","192.168.1.63","192.168.1.64","192.168.1.65","192.168.1.66","192.168.1.69"]

attackerShelfFile = '/home/var/log/attacker_shelf.dat'

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
                                       
# count files in a directory
# used for counting malware files captured by the honeynet                                       
def countFiles(path,globStr):

    try :
        fileCount = len(glob.glob1(path,globStr))
        return fileCount
        
    except Exception,e :
        msg = "attacker_statd.py : countFiles() : exception caught = " + `e`
        print msg
        syslog.syslog(msg)
        return None  
        
# Use ***incoming*** direction netflow records to update attack stats                                       
def updateAttackerOIDsNetflow(attacker,line) :
  
    try :      
        
        #print "attacker['IP'] is " + attacker['IP'].__str__()
         
        if line.find("dir=in") == -1 :
            return
        
        print "----"
        #print "attacker_statd.py : updateAttackerOIDsNetflow() : INCOMING : line=" + line[0:120] + "..."
        pat1 = 'dIP=(\d+\.\d+\.\d+\.\d+)'
        pat2 = 'sIP=(\d+\.\d+\.\d+\.\d+)'

        dip = re.findall(pat1,line)
        sip = re.findall(pat2,line)
                
        if len(dip) < 1 or len(sip) < 1 :	# could not find both a source IP and a dest IP
            return
        
        #print "attacker_statd.py : sip = " + sip.__str__()
        #print "attacker_statd.py : dip = " + dip.__str__()
            
        if dip[0] in honeypotIPs :
            #print "destination IP : " + dip[0] + " is a honeynet IP"
            #print "source IP : found attacker sIP : " + sip[0]
            
            # case 1 : update list of unique source IPs
            srcIP = sip[0]      
            #print srcIP
                
            # Weed out comms with Twitter, Google etc.
            print "attacker_statd.py : called hiddenIP() with IP = " + srcIP
            if kojoney_hiddenip.hiddenIP(srcIP) == True :
                print "attacker_statd.py : srcIP " + srcIP + " is not a real attacker since hiddenIP()=True, so ignore"
                return 
            else:
                print "attacker_statd.py : srcIP " + srcIP + " is an attacker since hiddenIP()=False, so update SNMP stats"
            
            if srcIP not in attacker['IP'] :
                #print srcIP + " not seen before"
                temp = attacker['IP']
                temp.append(srcIP)
                attacker['IP'] = temp
                #print "attacker['IP'] updated to : " + attacker['IP'].__str__()
                
                # increment number of unique IPs found 
                num = len(attacker['IP'])
                attacker['NUM_IP'] = num
                msg = "attacker['NUM_IP'] updated to " + attacker['NUM_IP'].__str__() + " by adding " + srcIP
                #print msg
                #syslog.syslog(msg)
                
                # case 2 : update list of unique country codes and cities
                geoIP = ipintellib.geo_ip(srcIP)
                countryCode = geoIP['countryCode']
                city = geoIP['city']
                
                if countryCode not in attacker['CC'] :
                    #print "attacker countryCode " + countryCode + " not seen before" 
                    temp = attacker['CC']
                    temp.append(countryCode)
                    attacker['CC'] = temp
                    msg = "attacker['CC'] updated to : " + attacker['CC'].__str__()
                    #print msg
                    
                    # increment number of unique CCs found 
                    num = len(attacker['CC'])
                    attacker['NUM_CC'] = num
                    msg = "attacker['NUM_CC'] updated to " + attacker['NUM_CC'].__str__() + " by adding " + countryCode
                    #print msg
                    #syslog.syslog(msg)
                
                if city not in attacker['CITY'] :
                    #print "attacker city " + city + " not seen before" 
                    temp = attacker['CITY']
                    temp.append(city)
                    attacker['CITY'] = temp
                    msg = "attacker['CITY'] updated to : " + attacker['CITY'].__str__()
                    #print msg
                    
                    # increment number of unique cities found 
                    num = len(attacker['CITY'])
                    attacker['NUM_CITY'] = num
                    msg = "attacker['NUM_CITY'] updated to " + attacker['NUM_CITY'].__str__() + " by adding " + city
                    #print msg
                    #syslog.syslog(msg)
                    
                # case 3 : update list of unique AS numbers
                asInfo = ipintellib.ip2asn(srcIP)
                asn = asInfo['as']
                if asn not in attacker['ASN'] :
                    #print "attacker ASN " + asn + " not seen before" 
                    temp = attacker['ASN']
                    temp.append(asn)
                    attacker['ASN'] = temp
                    msg = "attacker['ASN'] updated to : " + attacker['ASN'].__str__()
                    #print msg
                                        
                    # increment number of unique AS numbers 
                    num = len(attacker['ASN'])
                    attacker['NUM_ASN'] = num
                    msg = "attacker['NUM_ASN'] updated to " + attacker['NUM_ASN'].__str__()
                    #print msg
                    #syslog.syslog(msg)
                
                # case 4 : update list of unique /24
                slash24 = ipintellib.getSlash24(srcIP)
                if slash24 not in attacker['SLASH_24'] :
                    #print "attacker /24 " + slash24 + " not seen before" 
                    temp = attacker['SLASH_24']
                    temp.append(slash24)
                    attacker['SLASH_24'] = temp
                    msg = "attacker['SLASH_24'] updated to : " + attacker['SLASH_24'].__str__()
                    #print msg
                                        
                    # increment number of unique AS numbers 
                    num = len(attacker['SLASH_24'])
                    attacker['NUM_SLASH_24'] = num
                    msg = "attacker['NUM_SLASH_24'] updated to " + attacker['NUM_SLASH_24'].__str__() + " by adding " + slash24
                    #print msg
                    #syslog.syslog(msg)
        else:
            print "attacker_statd.py : dstIP " + dip[0] + " not found in honeypotList=" + honeypotIPs.__str__() + ", so no need to update attacker SNMP stats"             
        
        # All done so return
        return                 
    
    except Exception,e:    
        msg = "attacker_statd.py : updateAttackerOIDsNetflow() : exception caught = " + `e` + " line=" + line
        print msg
        syslog.syslog(msg)
                                   
# -------------------------------------------------------
        
# Start of code        
syslog.openlog("attacker_statd",syslog.LOG_PID,syslog.LOG_LOCAL2)         # Set syslog program name         
       
# Make pidfile so we can be monitored by monit        
pid =  makePidFile("attacker_statd")
if pid == None:
    syslog.syslog("Failed to create pidfile for pid " + `pid`)
    sys.exit(0)
else:
    syslog.syslog("attacker_statd.py started with pid " + `pid`)
    
attacker = shelve.open(attackerShelfFile)
if len(attacker) == 0 :		# contains no entries
    # 
    attacker['IP']           = []	# [0] List of IPs of Attackers	
    attacker['NUM_IP']       = 0	# Number of unique IPs of Attackers	
 
    attacker['CC']           = []   # List of Country Codes of Attackers
    attacker['NUM_CC']       = 0  	# List of Country Codes of Attackers
    
    attacker['ASN']          = []   # List of AS Numbers of Attackers
    attacker['NUM_ASN']      = 0 	# Number of AS Numbers of Attackers
    attacker['ASNAME']       = []	# List of AS Names of Attackers   	
    
    attacker['CITY']         = []	# List of Cities of Attackers   	
    attacker['NUM_CITY']     = 0	# Number of Cities of Attackers   	
    
    attacker['SLASH_24']     = []  # List of /24 subnets containing Attacker IPs
    attacker['NUM_SLASH_24'] = 0   # Number of /24 subnets containing Attacker IPs
    
    # Malware downloads
    attacker['AMUN_FILES_BIN']      = 0
    attacker['AMUN_FILES_HEX']      = 0
    attacker['NEPENTHES_FILES']     = 0
    attacker['KIPPO_FILES']         = 0 
    attacker['GLASTOPF_FILES_GET']  = 0
    attacker['GLASTOPF_FILES_POST'] = 0
    attacker['ANALYST_FILES_ALL']   = 0
    attacker['ANALYST_FILES_EXE']   = 0
    attacker['ANALYST_FILES_PHP']   = 0
    attacker['ANALYST_FILES_TXT']   = 0
    attacker['ANALYST_FILES_GIF']   = 0
    attacker['ANALYST_FILES_JPG']   = 0
    attacker['ANALYST_FILES_PNG']   = 0
    attacker['ANALYST_FILES_TGZ']   = 0
            
    print "case 1 : shelf file does not exist, so create a new one : attacker['IP'] is " + attacker['IP'].__str__()
    syslog.syslog("No attacker shelf file found, so created an empty one in " + attackerShelfFile)
else:
    #print "case 2 : exists : attacker['IP'] after is " + attacker['IP'].__str__()
    print "case 2 : using existing shelf file"
    syslog.syslog("attacker shelf file already exists, so will use it, filename=" + attackerShelfFile)
    
attacker.close()    
                
# files to monitor

netflowFilename = '/home/var/log/netflow.syslog'
netflowFile     = open(netflowFilename,'r')
            
# ------------
# tail -f mode
# ------------


# Find the size of the Netflow file and move to the end
st_resultsNetflow = os.stat(netflowFilename)
st_sizeNetflow    = st_resultsNetflow[6]
netflowFile.seek(st_sizeNetflow)

print "system     : Seek to end of Netflow file : " + netflowFilename

fileCheckCounter = 0
fileCounts = {}
try:

    while True:        

        # count malware collected
        # -----------------------
        fileCheckCounter = fileCheckCounter + 1
        #print "attacker_statd.py : main() : fileCheckCounter = " + fileCheckCounter.__str__()
        if fileCheckCounter >= 60 :
            fileCheckCounter = 0
            
            fileCounts['AMUN_FILES_BIN']      = countFiles("/usr/local/src/amun/malware/md5sum","*.bin")
            fileCounts['AMUN_FILES_HEX']      = countFiles("/usr/local/src/amun/hexdumps","*.hex")
            
            fileCounts['NEPENTHES_FILES']     = countFiles("/home/var/nepenthes/binaries","*")

            fileCounts['KIPPO_FILES']         = countFiles("/usr/local/src/kippo-0.5/dl","*")

            fileCounts['GLASTOPF_FILES_GET']  = countFiles("/usr/local/src/glastopf/files/get","*")
            fileCounts['GLASTOPF_FILES_POST'] = countFiles("/usr/local/src/glastopf/files/post","*")
            
            fileCounts['ANALYST_FILES_ALL']   = countFiles("/home/var/haxxor_webs/kojoney_analyst","*")
            fileCounts['ANALYST_FILES_EXE']   = countFiles("/home/var/haxxor_webs/kojoney_analyst","*.exe")
            fileCounts['ANALYST_FILES_PHP']   = countFiles("/home/var/haxxor_webs/kojoney_analyst","*.php")
            fileCounts['ANALYST_FILES_TXT']   = countFiles("/home/var/haxxor_webs/kojoney_analyst","*.txt")
            fileCounts['ANALYST_FILES_GIF']   = countFiles("/home/var/haxxor_webs/kojoney_analyst","*.gif")
            fileCounts['ANALYST_FILES_JPG']   = countFiles("/home/var/haxxor_webs/kojoney_analyst","*.jpg")
            fileCounts['ANALYST_FILES_PNG']   = countFiles("/home/var/haxxor_webs/kojoney_analyst","*.png")
            fileCounts['ANALYST_FILES_TGZ']   = countFiles("/home/var/haxxor_webs/kojoney_analyst","*.tgz")
            
            #print fileCounts
            
            # update the shelf
            attacker = shelve.open(attackerShelfFile)      
            for i in fileCounts :
                attacker[i] = fileCounts[i]
                #print i + " -> " + fileCounts[i].__str__()
                
            attacker.close()	# flushes to disk
            
            
        # look for events in Netflow file
        # -------------------------------
        whereNetflow = netflowFile.tell()
        line = netflowFile.readline().rstrip()
        if line :
            #print "attacker_statd.py : line read from Netflow log : " + line
            attacker = shelve.open(attackerShelfFile)
            updateAttackerOIDsNetflow(attacker,line)
            attacker.close()	# flushes to disk
                                    
        # delay
        # -----                                
        time.sleep(1)		

except Exception,e:
        print "attacker_statd.py : main() exception caught = " + `e` + " line=" + line
        syslog.syslog("attacker_statd.py : main() exception caught = " + `e` + " line=" + line)
