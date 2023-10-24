#!/usr/bin/python

import time, os , syslog , re 
import ipintellib
import kojoney_telnetd_idmef
import kojoney_attacker_event

#INFO: Running login_fail_exec 'echo Failed login from 81.218.144.234 with root:admin >> /tmp/ids.txt'                
#INFO: Running login_exec 'echo Successful login from 192.168.1.93 with root:123456 >> /tmp/ids.txt
#INFO: Running cmd_exec 'echo Command ran from 192.168.1.93 with root:123456: dir >> /tmp/ids.txt'

# return the Tweet or None
def processTelnetd(txnId,sensorId,line):
    
    try:
        addInfo1 = None
        addInfo2 = None
        
        line = line.rstrip('\n')
        #print line.rstrip('\n')

        if "echo Failed login from" not in line and "echo Successful login from" not in line and "echo Command ran from" not in line:
            return None
        
        #print "--------------------"
        print "processTelnetd() : " + line
        
        username = ""
        
        if "Failed" in line :
            success = False
        else:
            success = True    
                
        ips = re.findall("(\d+\.\d+\.\d+\.\d+)",line)
        if len(ips) > 0 :
            srcIP = ips[0]
        else:
           srcIP = "0.0.0.0"        
        #print "srcIP = " + srcIP

        geoIP = ipintellib.geo_ip(srcIP)                                
        countryCode = geoIP['countryCode'].__str__()                     
        
        c = re.findall("with (\S+)\:(\S+) ",line)
        if len(c) > 0 :
            username = c[0][0]
            password = c[0][1]
            #print c.__str__()
            #print "username : " + username
            #print "password : " + password
            addInfo1 = username
            addInfo2 = password
            
        if "login" in line:
            kojoney_telnetd_idmef.sendTelnetIDMEF(srcIP,"192.168.1.69","10023",username,password,success,line)
        
            # Update attacker database
            addInfo1 = username
            addInfo2 = password
            if success == True:
                kojoney_attacker_event.generateAttackerEvent(txnId,srcIP,None,sensorId,"GAINED_ACCESS","TELNETD",None,"Successful login",None,None,None,addInfo1,addInfo2)
            else:
                kojoney_attacker_event.generateAttackerEvent(txnId,srcIP,None,sensorId,"ATTACKING","TELNETD",None,"Failed login attempt",None,None,None,addInfo1,addInfo2)
        elif "Command" in line:	# attacker entered a command
            c = re.findall("with (\S+)\:(\S+)\: (\S+)",line)
            if len(c) > 0 :
                #username = c[0][0]
                #password = c[0][1]
                cmd = c[0][2]
                print "telnet command : [" + cmd + "]"
                addInfo1 = cmd
                addInfo2 = None
                kojoney_attacker_event.generateAttackerEvent(txnId,srcIP,None,sensorId,"MAINTAIN_ACCESS","TELNETD",None,"Attacker entered command",None,None,None,addInfo1,addInfo2)
        return None

    except Exception,e:
          msg = "processTelnetd() : exception : " + e.__str__()
          print msg
          syslog.syslog(msg)

        
# Start of code
# This is a test harness so comment/uncomment the relevent lines        
        
if __name__ == '__main__' :
       
# Set the input file to scan
    filename = '/home/var/log/faketelnetd.log'
    
    file = open(filename,'r')

    while True:
    
        # Tweets log file       
        # where = file.tell()
        line  = file.readline()
        line=line.rstrip('\n')
        
        if not line:		# no data to process
            pass
        else :			# new data has been found
            msg = processTelnetd(777,"TEST",line)
            
        if msg != None:
            print "line after parsing = [" + msg +"]"
                       
        #print "sleeping..."
        # this can be a float for sub-second sleep    
        time.sleep(0.2)		# 0.1 
                              
                 