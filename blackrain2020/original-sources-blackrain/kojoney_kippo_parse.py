#!/usr/bin/python


import time, os , syslog , re , sys 
import ipintellib
import kojoney_kippo_idmef
import kojoney_attacker_event
import simplejson as  json

#2011-01-07 21:00:16+0000 [SSHChannel session (0) on SSHService ssh-connection on HoneyPotTransport,1,192.168.1.75] Opening TTY log: log/tty/20110107-210016-9013.log
#2011-01-07 21:00:46+0000 [SSHChannel session (0) on SSHService ssh-connection on HoneyPotTransport,1,192.168.1.75] CMD: who
#2011-01-07 21:00:46+0000 [SSHChannel session (0) on SSHService ssh-connection on HoneyPotTransport,1,192.168.1.75] Command found: who
#2011-01-07 21:00:59+0000 [SSHChannel session (0) on SSHService ssh-connection on HoneyPotTransport,1,192.168.1.75] CMD: top
#2011-01-07 21:00:59+0000 [SSHChannel session (0) on SSHService ssh-connection on HoneyPotTransport,1,192.168.1.75] Command not found: top
#2011-01-07 21:01:01+0000 [SSHChannel session (0) on SSHService ssh-connection on HoneyPotTransport,1,192.168.1.75] CMD: ls
#2011-01-07 21:01:01+0000 [SSHChannel session (0) on SSHService ssh-connection on HoneyPotTransport,1,192.168.1.75] Command found: ls
#2011-01-07 21:01:03+0000 [SSHChannel session (0) on SSHService ssh-connection on HoneyPotTransport,1,192.168.1.75] CMD: pwd
#2011-01-07 21:01:03+0000 [SSHChannel session (0) on SSHService ssh-connection on HoneyPotTransport,1,192.168.1.75] Command found: pwd
#2011-01-07 21:01:06+0000 [SSHChannel session (0) on SSHService ssh-connection on HoneyPotTransport,1,192.168.1.75] CMD: id
#2011-01-07 21:01:06+0000 [SSHChannel session (0) on SSHService ssh-connection on HoneyPotTransport,1,192.168.1.75] Command found: id

#2013-05-08 05:51:23+0100 [SSHChannel session (0) on SSHService ssh-connection on HoneyPotTransport,74,192.168.1.73] CMD: passwd
#2013-05-08 05:51:23+0100 [SSHChannel session (0) on SSHService ssh-connection on HoneyPotTransport,74,192.168.1.73] Command found: passwd
#2013-05-08 05:51:29+0100 [SSHChannel session (0) on SSHService ssh-connection on HoneyPotTransport,74,192.168.1.73] INPUT (passwd): fake
#2013-05-08 05:51:30+0100 [SSHChannel session (0) on SSHService ssh-connection on HoneyPotTransport,74,192.168.1.73] INPUT (passwd): fake

def processKippo(txnId,sensorId,line):

    try :
        line=line.strip("\n")
        print "############################################"
        print "processKippo() : line received from Honeypot : " + line
        addInfo1 = None
        addInfo2 = None
                
        # log succeeded attempted passwords to a file            
        if line.find("login attempt") != -1 and line.find("succeeded") != -1 :
            pat = '\d+\.\d+\.\d+\.\d+'
            attacker = re.findall(pat,line)
            if len(attacker) == 1 :
                srcIP = attacker[0]
            else :
                srcIP = "0.0.0.0"    
            geoIP = ipintellib.geo_ip(srcIP)
            countryCode = geoIP['countryCode'].__str__()
            
            fields = line.split(" ")
            #print fields
            a = fields[8]		# e.g. [root/123456]
            a = a.lstrip("[")
            a = a.rstrip("]")
            username = a.split('/')[0]
            password = a.split('/')[1]
            
            #print "login OK : credentials = " + username + " " + password
            msg = srcIP + ":" + countryCode + "," + username + ":" + password + ",succeeded" + ",kippo"
            print msg
            
            # Fake auth.log entry for use by OSSEC :-
            # Accepted password for crouchr from 192.168.1.73 port 46366 ssh2
            tstamp = time.ctime()
            fields = tstamp.split(" ")
            print "kojoney_kippo_parse.py : fields=" + fields.__str__()
            
            tstamp = fields[1] + " " + fields[2] + " " + fields[3]
            fakeAuthLogMsg = tstamp + " mars sshd[12345]: Accepted password for " + username + " from " + srcIP + " port 12345 ssh2"
            print "kojoney_kippo_parse.py : fakeAuthLogMsg : " + fakeAuthLogMsg
            fp = open("/home/var/log/kippo_auth.log",'a')
            print >> fp, fakeAuthLogMsg
            fp.close()
            
            # Send event to SIEM
            kojoney_kippo_idmef.sendSshIDMEF(srcIP,"192.168.1.64","2222",username,password,True,line)

            # Send to syslog to be picked up by logstash
            #sdata = {}
            #sdata['username'] = username
            #sdata['password'] = password
            #sdata['ip']       = srcIP.__str__()
            #sdata['phase']    = "GAINED_ACCESS"
            #syslog.openlog("kojoney_kippo")
            #syslog.syslog(json.dumps(sdata))   

            # Update attacker database
            addInfo1 = username
            addInfo2 = password
            kojoney_attacker_event.generateAttackerEvent(txnId,srcIP,None,sensorId,"GAINED_ACCESS","KIPPO",None,"Successful login",None,None,None,addInfo1,addInfo2)

            fp = open("/home/var/secviz/failedCredentialsViz.csv",'a')
            print >> fp, msg
            fp.close()
            
        # log failed attempted passwords to a file            
        if line.find("login attempt") != -1 and line.find("failed") != -1 :
            pat = '\d+\.\d+\.\d+\.\d+'
            attacker = re.findall(pat,line)
            if len(attacker) == 1 :
                srcIP = attacker[0]
            else :
                srcIP = "0.0.0.0"    
            geoIP = ipintellib.geo_ip(srcIP)
            countryCode = geoIP['countryCode']
            
            fields = line.split(" ")
            #print fields
            a = fields[8]		# e.g. [root/123456]
            a = a.lstrip("[")
            a = a.rstrip("]")
            username = a.split('/')[0]
            password = a.split('/')[1]
            if len(password) == 0 :
                password = "<NONE_ENTERED>"
                
            #print "login FAIL : credentials = " + username + " " + password
            msg = srcIP + ":" + countryCode + "," + username + ":" + password + ",failed" + ",kippo" + "," + time.ctime()
            print msg

            # Fake FAILED auth.log entry for use by Ossec :-
            # Failed password for user crouchr from 192.168.1.73 port 46366 ssh2
            tstamp = time.ctime()
            fields = tstamp.split(" ")
            tstamp = fields[1] + " " + fields[2] + " " + fields[3]
            fakeAuthLogMsg = tstamp + " mars sshd[12345]: Failed password for user " + username + " from " + srcIP + " port 12345 ssh2"
            fakeAuthLogMsg = fakeAuthLogMsg.replace("2013 ","")
            print "fakeAuthLogMsg : " + fakeAuthLogMsg
            # Update clone of auth.log so OSSEC standard SSH rules can be used           
            fp = open("/home/var/log/kippo_auth.log",'a')
            print >> fp, fakeAuthLogMsg
            fp.close()
            
            # Send event to SIEM
            kojoney_kippo_idmef.sendSshIDMEF(srcIP,"192.168.1.64","2222",username,password,False,line)

            # Send to syslog to be picked up by logstash
            #sdata = {}
            #sdata['username'] = username
            #sdata['password'] = password
            #sdata['ip']       = srcIP.__str__()
            #sdata['phase']    = "ATTACKING"
            #syslog.openlog("kojoney_kippo")
            #syslog.syslog(json.dumps(sdata))   
            
            # Update attacker database
            addInfo1 = username
            addInfo2 = password
            kojoney_attacker_event.generateAttackerEvent(txnId,srcIP,None,sensorId,"ATTACKING","KIPPO",None,"Failed login attempt",None,None,None,addInfo1,addInfo2)

            fp = open("/home/var/secviz/failedCredentialsViz.csv",'a')
            print >> fp, msg
            fp.close()
        
        # Also add INPUT - i.e. if user performs a passwd
        # Received unhandled keyID => attacker is a human
        if (line.find("Opening TTY log") == -1 and line.find("CMD:") == -1 and  line.find("Received unhandled keyID") == -1) :         # can't find the interesting entries so return 
            return None
        
        # Human keystrokes (backspace etc.) detected ?
        if  "Received unhandled keyID" in line :
            ip = re.findall("(\d+\.\d+\.\d+\.\d+)",line)
            if len(ip) > 0 :
                srcIP = ip[0]
            else:
                srcIP = "0.0.0.0"    
            kojoney_attacker_event.generateAttackerEvent(txnId,srcIP,None,sensorId,"HUMAN_ACTIVITY","KIPPO",None,"Attacker is a human",None,None,None,addInfo1,addInfo2)
            return None
                
        #print "processKippo() : candidate syslog read from Honeypot : " + line
                                                                                 
        fields = line.split()
        #print fields
        
        uid = "0"		# Kippo only supports a root account
        a = fields[9].rstrip(']')
        srcip = a.split(',')[2]
        #print "Attacker IP : " + srcip

        # INT = intrusion
        if line.find("Opening TTY log") != -1:
            tweet = "KIPPO_INT," + "login from " + srcip + " to be logged in " + fields[13] 
        else:
            cmd = ' '.join(fields[11:])
            #cmd = 'rch testing - ignore'
            print "kojoney_kippo_parse.py : cmd=[" + cmd.__str__() + "]"
        
            ip = re.findall("(\d+\.\d+\.\d+\.\d+)",line)
            if len(ip) > 0 :
                srcIP = ip[0]
            else:
                srcIP = "0.0.0.0"    
            geoIP = ipintellib.geo_ip(srcIP)
            countryCode = geoIP['countryCode'].__str__()
            
            #print "kojoney_kippo_parse.py : Attacker " + srcIP + " from " + countryCode + " typed : " + cmd
            
            # fake the correct shell prompt
            if uid == "0" :
                prompt = "#"
            else:
                prompt = "$"
            #tweet = "--,KIPPO,UID:" + uid + " {sshd} " + prompt + " " + cmd	# fake the GeoIP of src (unknown)
            tweet = "KIPPO,UID:" + uid + " {sshd} " + prompt + " " + cmd	# fake the GeoIP of src (unknown)
            
            kojoney_kippo_idmef.sendSshCmdIDMEF(srcIP,"192.168.1.64","2222",uid,prompt + " " + cmd,line)
            
            # Log all commands to a file
            msg = time.ctime() + "," + srcIP + "," + countryCode.__str__() + "," + cmd
            fpCmds = open("/home/var/log/kippo-all-cmds.csv","a")
            print >> fpCmds,msg
            fpCmds.close()
            
            # Update Attacker Database
            addInfo1 = cmd
            addInfo2 = None
            if "wget " in cmd.lower() :			# Use trailing space to force an argument to have been supplied for wget etc.
                kojoney_attacker_event.generateAttackerEvent(txnId,srcIP,None,sensorId,"MAINTAIN_ACCESS","KIPPO",None,"Attacker attempted to retrieve malware",None,None,None,addInfo1,addInfo2)
            elif "apt-get install " in cmd.lower():	# Use trailing space to force an argument to have been supplied for wget etc.
                kojoney_attacker_event.generateAttackerEvent(txnId,srcIP,None,sensorId,"MAINTAIN_ACCESS","KIPPO",None,"Attacker attempted to install software",None,None,None,addInfo1,addInfo2)
            elif "chmod " in cmd.lower() or "tar " in cmd.lower():	# Use trailing space to force an argument to have been supplied for wget etc.
                kojoney_attacker_event.generateAttackerEvent(txnId,srcIP,None,sensorId,"MAINTAIN_ACCESS","KIPPO",None,"Attacker attempted to install software",None,None,None,addInfo1,addInfo2)
            elif "perl " in cmd.lower() or "sh " in cmd.lower() or "python " in cmd.lower() or "./" in cmd.lower():	# Use trailing space to force an argument to have been supplied for wget etc.
                kojoney_attacker_event.generateAttackerEvent(txnId,srcIP,None,sensorId,"MAINTAIN_ACCESS","KIPPO",None,"Attacker attempted to execute software",None,None,None,addInfo1,addInfo2)
            elif "rm " in cmd.lower() :			# Use trailing space to force an argument to have been supplied for wget etc.
                kojoney_attacker_event.generateAttackerEvent(txnId,srcIP,None,sensorId,"COVER_TRACKS","KIPPO",None,"Attacker attempted to delete file",None,None,None,addInfo1,addInfo2)
            elif "passwd" in cmd.lower() :		
                kojoney_attacker_event.generateAttackerEvent(txnId,srcIP,None,sensorId,"COVER_TRACKS","KIPPO",None,"Attacker attempted to modify password",None,None,None,addInfo1,addInfo2)
            elif "adduser" in cmd.lower() :		
                kojoney_attacker_event.generateAttackerEvent(txnId,srcIP,None,sensorId,"COVER_TRACKS","KIPPO",None,"Attacker attempted to add user",None,None,None,addInfo1,addInfo2)
            elif "apt-get remove " in cmd.lower():	# Use trailing space to force an argument to have been supplied for wget etc.
                kojoney_attacker_event.generateAttackerEvent(txnId,srcIP,None,sensorId,"COVER_TRACKS","KIPPO",None,"Attacker attempted to uninstall software",None,None,None,addInfo1,addInfo2)
            elif "reboot" in cmd.lower():		# Use trailing space to force an argument to have been supplied for wget etc.
                kojoney_attacker_event.generateAttackerEvent(txnId,srcIP,None,sensorId,"COVER_TRACKS","KIPPO",None,"Attacker attempted to reboot node",None,None,None,addInfo1,addInfo2)
            elif "shutdown " in cmd.lower():		# Use trailing space to force an argument to have been supplied for wget etc.
                kojoney_attacker_event.generateAttackerEvent(txnId,srcIP,None,sensorId,"COVER_TRACKS","KIPPO",None,"Attacker attempted to shutdown node",None,None,None,addInfo1,addInfo2)
                
        print "processKippo() : tweet=" + tweet 
        return tweet
    
    except Exception,e:
        syslog.syslog("kojoney_tweet.py : processKippo() exception caught = " + `e` + " line=" + line)


if __name__ == '__main__' :
    
    filename = '/home/var/log/kippo.log'
    file = open(filename,'r')
    
    while True :
        line=file.readline()
        if not line :
            pass
        else:
            msg = processKippo(666,"TEST",line)
            
        if msg != None :
            print msg
            
        #time.sleep(0.2)
                                                                                