#!/usr/bin/python

import time, os , syslog , re 
import kojoney_funcs
import kojoney_afterglow
import ipintellib
import kojoney_glastopf_idmef
import kojoney_idmef_common
import kojoney_attacker_event

#2012-09-21 16:11:48,612 - GlastopfLogger - INFO - GET attack from 204.232.248.45 with request: /wp-content/plugins/uBillboard/?src=http://img.youtube.com.alsahil
#2012-09-23 00:38:40,028 - GlastopfLogger - INFO - No attack found from 123.139.175.253 with request: http://www.baidu.com/
#2012-09-25 18:24:08,785 - GlastopfLogger - INFO - No attack found from 60.244.114.4 with request: /admin/sqlpatch.php/password_forgotten.php?action=execute
#2012-09-23 09:34:23,752 - GlastopfLogger - INFO - http://blogger.com.trd.hu/both.php successfully opened
#2012-09-23 09:34:24,124 - GlastopfLogger - INFO - File 808872b025205a28929653216b2ef6b8 written to disk
# return the Tweet or None

def processGlastopf(txnId,sensorId,line):
    
    asMsg = ""
    
    try :
        print "-------------\nprocessGlastopf() : line read is " + line
        dstIP   = "192.168.1.62" # bug - not portable
        request = "No URL found"
        apacheCLF = "None"
        
        logEntry = line	# keep a copy since we are going to modify line
        
        # Normalise Mail attacks
        line = line.replace("ail attack found","ail attack from")
        
        # Looks like a duplication bug so ignore the 'Unknown' variant
        if "Unknown POST attack" in line:
            return None
        
        # ATTACK : Successful attack
        if line.find("attack from") != -1 or line.find("Mail attack found from") != -1 :
            print "WebApp attack detected : " + line
            apacheCLF = fakeApacheCLF(line)					# fake an Apache CLF record
            fields    = line.split(" - ")
            #print fields
            msg = ' '.join(fields[3:])
            #msg = ' '.join(fields[3:]).rstrip("?")		# does glastopf add trailing ? / ??
            msg = "WEB_X," + msg
            msg = msg.replace(" with request: "," req=")
            #msg = msg.replace("found from","from")		# normalise MAIL versus "other" attacks
            msg = msg.replace("Mail","Webmail")			# normalise MAIL versus "other" attacks
          
            msg = msg.replace("/","|")	# fool Twitter into not using t.co URL shortening and ensure users cannot click on malware links
            
            a = re.findall("(GET|POST|Unknown POST|Mail) attack from",line)
            if len(a) > 0 :
                attackType = "WebApp " + a[0].upper() + "-based RFI attack"	# upper() used to convert Mail to MAIL    
            else:
                attackType = "Unknown WebApp attack"
             
            ips = re.findall("from (\d+\.\d+\.\d+\.\d+)",line)
            if len(ips) > 0:
                srcIP = ips[0]
                if "request" in line:
                    request = line.split("request: ")[1]
                print "Successful WebApp attack : AttackType=" + attackType + " srcIP=" + srcIP + " URLrequest=" + request
            
            if "unknown" in line.lower():
                completion = "failed"
            else:
                completion = "succeeded"
                          
            kojoney_glastopf_idmef.sendWebAppIDMEF(attackType,request,"http","18080",completion,srcIP,dstIP,apacheCLF,srcIP,logEntry)
            kojoney_attacker_event.generateAttackerEvent(txnId,srcIP,None,sensorId,"ATTACKING","GLASTOPF",None,attackType,None,None,None,apacheCLF,None)
                    
            return msg
            

        # File retrieved
        if line.find("successfully opened") != -1 :
            #apacheCLF=fakeApacheCLF(line)					# fake an Apache CLF record
            fields = line.split(" - ")
            #print fields
            msg = ' '.join(fields[3:])
            msg = "WEB_OPEN," + msg
            urls = re.findall("(\S+) successfully opened",line)
            if len(urls) > 0 :
                url = urls[0]
                domain = kojoney_idmef_common.extractDomain(url)
                if domain != None:
                    dnsInfo = ipintellib.ip2name(domain)  
                    dstIP = dnsInfo['name']
                else:
                    dstIP = "0.0.0.0"	# error    
                # IDMEF the honeypot to drop-site flow
                kojoney_glastopf_idmef.sendWebAppURLIDMEF("WebApp URL opened",url,"http","192.168.1.62",dstIP,"80","succeeded","None",dstIP,logEntry)
          
            msg = msg.replace("/","|")	# fool Twitter into not using t.co URL shortening and ensure users cannot click on malware links
            
            return msg

        # Googledorks data written to mySQL database - not interesting enough to Tweet
        #if line.find("written into local database") != -1 :
        #    fields = line.split(" - ")
        #    #print fields
        #    msg = ' '.join(fields[3:])
        #    msg = "WEB_GOOGLEDORK," + msg
        #    return msg

        # File saved to disk
        if line.find("written to disk") != -1 and line.find("File ") != -1 :
            fields = line.split(" - ")
            #print fields
            msg = ' '.join(fields[3:])
            msg = msg.replace("File","Previously unseen PHP malware file")
            msg = "WEB_WRITE," + msg
            fileMD5 = fields[3].split(" ")[1]
            kojoney_glastopf_idmef.sendWebAppFile("File retrieved from remote server",fileMD5,logEntry)
            return msg

        # Scan - i.e. unsuccessful attack
        if line.find("No attack found") != -1 :
            apacheCLF=fakeApacheCLF(line)						# fake an Apache CLF record
            #print "scan"
            ip = kojoney_funcs.findFirstIP(line)
            if ip != None:
                #print "IP found = " + ip
                # WHOIS information
                #asInfo = rch_asn_funcs.ip2asn(ip)
                asInfo = ipintellib.ip2asn(ip)
                asNum =  asInfo['as']                                   # AS123 
                asRegisteredCode = asInfo['registeredCode']             # Short-form e.g.ARCOR
                asMsg = asRegisteredCode + " (" + asNum + ")"
                #print asMsg                         
                                                     
            fields = line.split(" - ")
            #print fields
            msg = ' '.join(fields[3:])
            if line.find("http") != -1 :	# attacker is trying to test if I am a proxy
                msg = msg.replace("No attack found from","WEB_PRX,Request from")
                attackType = "WebApp proxy scan"
            else:				# LOC = local
                msg = msg.replace("No attack found from","WEB_SCN,Scan from")
                attackType = "WebApp scan"
            msg = msg.replace(" with request: "," req=")
            msg = msg.rstrip();	# remove any trailing characters
            #msg = msg + " ISP=" + asMsg
            kojoney_afterglow.visWebScan(msg)
            
            msg = msg.replace("/","|")	# fool Twitter into not using t.co URL shortening and ensure users cannot click on malware links
            
            ips = re.findall("from (\d+\.\d+\.\d+\.\d+)",line)
            if len(ips) > 0:
                srcIP = ips[0]
                request = line.split("request: ")[1]
                #print attackType + " : srcIP : " + srcIP + " request : " + request
                # go for two events ?
                if attackType == "WebApp proxy scan" :
                    kojoney_glastopf_idmef.sendWebAppURLIDMEF("WebApp proxy scan Request",request,"http",srcIP,"192.168.1.62","18080","failed",apacheCLF,srcIP,logEntry)	# inbound
                    kojoney_attacker_event.generateAttackerEvent(txnId,srcIP,None,sensorId,"SCANNING","GLASTOPF",None,"WebApp proxy scan Request",None,None,None,apacheCLF,None)
                    domain = kojoney_idmef_common.extractDomain(request)
                    if domain != None:
                        dnsInfo = ipintellib.ip2name(domain)  
                        dstIP = dnsInfo['name']
                    else:
                        dstIP = "0.0.0.0"	# error
                    kojoney_glastopf_idmef.sendWebAppURLIDMEF("WebApp proxy scan Retrieval",request,"http","192.168.1.62",dstIP,"80","failed",apacheCLF,dstIP,logEntry)		# outbound
                    kojoney_attacker_event.generateAttackerEvent(txnId,srcIP,None,sensorId,"SCANNING","GLASTOPF",None,"WebApp proxy scan Retrieval",None,None,None,apacheCLF,None)
                else:
                    kojoney_glastopf_idmef.sendWebAppURLIDMEF(attackType,request,"http",srcIP,"192.168.1.62","18080","failed",apacheCLF,srcIP,logEntry)				# inbound
                    kojoney_attacker_event.generateAttackerEvent(txnId,srcIP,None,sensorId,"SCANNING","GLASTOPF",None,"WebApp scan",None,None,None,apacheCLF,None)
            return msg
                    
        return None

    except Exception,e:
                msg = "kojoney_glastopf_parse.py : processGlastopf() : " + `e` + " line=" + line
                print msg
                syslog.syslog(msg)


# INPUT FORMAT
#2012-08-21 15:46:20,679 - GlastopfLogger - INFO - No attack found from 62.152.59.202 with request: /snews/visualiza.php?id='
#2012-09-10 23:39:55,408 - GlastopfLogger - INFO - GET attack from 23.29.120.187 with request: //administrator/components/com_jpack/includes/CAltInstaller.php?mosConfig_absolut
#e_path=http://www.airportfootprints.net//wp-content/themes/TheTravelTheme/includes/cache/l??

# OUTPUT FORMAT - taken from real Apache
#192.168.1.180 - - [13/Feb/2012:21:00:28 +0000] "GET /banner.htm HTTP/1.1" 200 929
#192.168.1.180 - - [13/Feb/2012:21:00:29 +0000] "GET /main.htm HTTP/1.1" 200 3338
#192.168.1.180 - - [13/Feb/2012:21:00:29 +0000] "GET /images/brown_background.gif HTTP/1.1" 200 6732
#192.168.1.180 - - [13/Feb/2012:21:00:33 +0000] "GET /favicon.ico HTTP/1.1" 404 209
#192.168.1.180 - - [13/Feb/2012:21:00:34 +0000] "GET /favicon.ico HTTP/1.1" 404 209
#192.168.1.180 - - [13/Feb/2012:21:00:34 +0000] "GET /favicon.ico HTTP/1.1" 404 209
#192.168.1.180 - - [13/Feb/2012:21:00:54 +0000] "GET /info.php HTTP/1.1" 404 206
# Produce an Apache CLF (Common Log Format) compatible log so that 
# existing Apache Log inspection software (Ossec/Prelude-LML) can be used out of the box
def fakeApacheCLF(line):
    MONTH = ['None','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    try :
        #print "-----\nEntered fakeApacheCLF() : line = " + line
        # extract source IP (attacker)
        ips = re.findall("\d+\.\d+\.\d+\.\d+",line)
        if len(ips) > 0 :
            srcip = ips[0]
        else:
            return None
            
        if "request" not in line:
            return None
               
        # Extract the request
        header  = line.split("request: ")[0]
        request = line.split("request: ")[1].rstrip()
        
        dateV = header.split(" ")[0]
        timeV = header.split(" ")[1]
        timeV = timeV.split(",")[0]
        
        #print "srcip   : " + srcip
        #print "dateV   : " + dateV
        #print "timeV   : " + timeV
        #print "request : " + request
 
        yearV  = dateV.split("-")[0]
        monthV = dateV.split("-")[1]
        dayV   = dateV.split("-")[2]
        
        apacheTimestamp = "[" + dayV + "/" + MONTH[int(monthV)] + "/" + yearV + ":" + timeV + " +0000" + "]" 
        #print apacheTimestamp
        
        apacheCLF = srcip + " - - " + apacheTimestamp + " " '"' + "GET " + request + " HTTP/1.1" + '"' + " " + "200" + " " + "666"
        
        # try and force some OSSEC events using HTTP code 500 -> this worked
        # apacheCLF = srcip + " - - " + apacheTimestamp + " " '"' + "GET " + request + " HTTP/1.1" + '"' + " " + "500" + " " + "666"
        
        #print "fakeApacheCLF constructed : " + apacheCLF.__str__()
        #if writeFlag == True :
        apacheLog = open("/home/var/log/httpd/access_log","a")  
        print >> apacheLog,apacheCLF
        print "ApacheCLF : " + apacheCLF
        apacheLog.close()
        
        return apacheCLF      
          
    except Exception,e :
      msg = "kojoney_glastopf_parse.py : fakeApacheCLF() : " + `e` + " line=" + line
      print msg
      syslog.syslog(msg)
      return None

                               
# -------------------------------------------------------
        
# Start of code
# This is a test harness so comment/uncomment the relevent lines        
        
if __name__ == '__main__' :
       
# Set the input file to scan
    filename = '/usr/local/src/glastopf/log/glastopf.log'
    file = open(filename,'r')
    txnId = -1
    sensorId = "TEST"
    
    while True:
        txnId = txnId + 1
        # Tweets log file       
        # where = file.tell()
        line  = file.readline()
        line  = line.rstrip('\n')
        
        if not line:		# no data to process
            pass
        else :			# new data has been found
            if "GET"  in line.upper():
            #if "POST" in line.upper():
            #if "MAIL" in line.upper():
            #if "successfully opened" in line:
            #if "o attack found" in line:
            #if "File " in line and "written to disk" in line:
                msg = processGlastopf(txnId,sensorId,line)
            
        #if msg != None:
        #    print "*** Tweet : " + msg
                       
        #print "sleeping..."
        # this can be a float for sub-second sleep    
        time.sleep(0.1)		# 0.1 
                              
