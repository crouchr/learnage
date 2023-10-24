#!/usr/bin/python

import time, os , syslog , re 
import kojoney_amun_idmef
import kojoney_idmef_common
import ipintellib

# 2011-11-05 10:22:57,764 INFO removing successfull exploit IP 120.75.5.84 (blocktime: 7200)
# 2011-11-05 18:55:49,874 INFO removing successfull exploit IP 79.113.51.37 (blocktime: 7200)
# 2011-11-05 18:55:53,918 INFO removing successfull download IP 79.113.51.37 (blocktime: 7200)
# 2011-11-05 20:03:37,501 INFO sending shutdown to idle connection (idle: 120 IP: 81.213.73.145)
# 2011-11-05 22:03:37,894 INFO removing successfull exploit IP 81.213.73.145 (blocktime: 7200)
# 2011-11-05 22:03:51,979 INFO removing successfull download IP 146.185.246.88 (blocktime: 7200)
# above entries are in amun_server.log 

#2010-09-27 18:49:01,487 INFO [submit_md5] download (http://208.53.183.171:80/h.exe): 748610496089bcb82b95fe67062f314c (size: 94208) - MS08067
#2010-09-27 18:49:07,532 INFO [submit_anubis] anubis result: http://anubis.iseclab.org/?action=result&task_id=1e285a7544512cd4439e2fcbc0d52c2e7
# return the Tweet or None
def processAmunSubmit(line):
    
    try :
        #print "processAmunSubmit() : line read is " + line

        # Crude attempt to not Tweet error messages from the malware analysis sites
        if line.find("problem") != -1 :		# Cwsandbox "Due to repeated hardware problems..."
            return None
        if line.find("error") != -1 :		# not seen explicitly - just a guess
            return None

        if line.find("anubis result") != -1 :
            fields = line.split(",")
            msg = fields[1].split(" ")
            #print msg
            msg = ' '.join(msg[5:])
            #msg = "AMUN_ANALYSIS,Anubis Analysis : " + msg
            msg = msg.replace(","," ")	# commas break tweet engine at the moment
            msg = "AMUN_AA,Analysis : " + msg
            return msg

        # CWSandbox is not as reliable as Anubis but it does return text error messages
        if line.find("cwsandbox result") != -1 :
            fields = line.split(",")
            msg = fields[1].split(" ")
            #print msg
            msg = ' '.join(msg[5:])
            #msg = "AMUN_ANALYSIS,CWSandbox Analysis : " + msg
            msg = "AMUN_AC,Analysis : " + msg
            msg = msg.replace(","," ")  # commas break tweet engine at the moment
            return msg
            
        # get one of these is Amun has not seen this MD5 before i.e. new sample
        # not that interesting so filter out
        #if line.find("download") != -1 :
        #    fields = line.split(",")
        #    msg = fields[1].split(" ")
        #    print msg
        #    msg = ' '.join(msg[3:])
        #    msg = "AMUN_S," + msg
        #    return msg

        return None

    except Exception,e:
                syslog.syslog("kojoney_amun_parse.py : processAmunSubmit() : " + `e` + " line=" + line)

# return the Tweet or None
#2010-04-26 09:53:28,660 INFO exploit 217.115.189.123:4626 -> 192.168.1.66:135 (DCOM Vulnerability: tftp://217.115.189.123:69/ssms.exe) (Shellcode: leimbach)
def processAmunExploit(line):
    
    try :
        #print "processAmunExploit() : line read is " + line

        # Ignore if do not find shellcode in the exploit
        #if line.find("Shellcode: None") != -1 :
        #    return None
        
        # First IP is attacker IP    
        pat = '(\d+\.\d+\.\d+\.\d+)\:(\d+)'
        
        ips = re.findall(pat,line)
        #print "srcIP = " + srcIP[0].__str__()  
        if len(ips) > 0 :
            #print ips
            srcIP   = ips[0][0]
            srcPort = ips[0][1]
            dstIP   = ips[1][0]
            dstPort = ips[1][1]
            
            #print srcIP + " : " + srcPort
            #print dstIP + " : " + dstPort

        vulns = re.findall('(\w+) Vulnerability',line)
        #print vulns

        # This is actually the callback URL
        info = re.findall('Vulnerability\: (\S+)',line)
        #vulns[0] = vulns[0].rstrip(')')
        info[0] = info[0].rstrip(')')		
        #print info
        
        shellcode = re.findall('Shellcode: (\w+)',line)
        #print shellcode
        
        # IDMEF #1 : send info about the attacker to Prelude SIEM
        kojoney_amun_idmef.exploitIDMEF(srcIP,srcPort,dstIP,dstPort,vulns[0],info[0],shellcode[0],line)
        
        # IDMEF #2 : send info about the drop-site to Prelude SIEM
        domain = kojoney_idmef_common.extractDomain(info[0])
        if domain != None :
            a = re.findall("(\d+\.\d+\.\d+\.\d+)",domain)
            if len(a) > 0 :
                dstIP = domain
            else:
                dnsInfo = ipintellib.ip2name(domain)
                dstIP = dnsInfo['name']
        #else:
        #    dstIP = "0.0.0.0"   # error 
            kojoney_amun_idmef.exploitDropsiteIDMEF("192.168.1.66",dstIP,srcIP,info[0],line)
        
        # Ignore if do not find any shellcode in the exploit
        if line.find("Shellcode: None") != -1 :
            return None

        # some filenames have these brackets around the last part for some reason
        line = line.replace("['","")
        line = line.replace("']","")
        line = line.replace("(","")
        line = line.replace(")","")

        fields = line.split(",")
        #print fields
                
        msg = fields[1].split(" ")
        #print msg
        msg = ' '.join(msg[5:])
        
        msg = srcIP[0].__str__() + "->" + msg
        msg = msg.replace("192.168.1.66"   , "AMUN")
        msg = msg.replace("Vulnerability:" , "vulnerability")
        msg = msg.replace("Shellcode: "    , "shellcode=")
            
        msg = "AMUN_X," + msg
    
        return msg

    except Exception,e:
        error = "kojoney_amun_parse.py : processAmunExploit() : " + `e` + " line=" + line
        print error
        syslog.syslog(error)
                
# return the Tweet or None
def processAmunDownload(line):
    
    try:
        #print "processAmunDownload() : line read is " + line

        if line.find("INFO download") == -1 :
            return None
        # now I know it decodes OK, does not add much additional information
        return None

        fields = line.split(",")
    
        msg = fields[1].split(" ")
        #print msg
        msg = ' '.join(msg[3:])
    
#       msg = "AMUN_D/LOAD," + msg
        msg = "AMUN_D," + msg
    
        return msg

    except Exception,e:
        syslog.syslog("kojoney_amun_parse.py : processAmunDownload() : " + `e` + " line=" + line)
                               
# -------------------------------------------------------
        
# Start of code
# This is a test harness so comment/uncomment the relevent lines        
        
if __name__ == '__main__' :
       
# Set the input file to scan
    #filename = '/usr/local/src/amun/logs/testcases/submissions.log'
    #filename = '/usr/local/src/amun/logs/testcases/exploits.log'
    filename = '/usr/local/src/amun/logs/testcases/successfull_downloads.log'
    file = open(filename,'r')

    while True:
    
        # Tweets log file       
        # where = file.tell()
        line  = file.readline()
        line=line.rstrip('\n')
        
        if not line:		# no data to process
            pass
        else :			# new data has been found
            #print "line before parsing = [" + line + "]"
            #msg = processAmunSubmit(line)
            #msg = processAmunExploit(line)
            msg = processAmunDownload(line)
        
        if msg != None:
            print "line after parsing = [" + msg +"]"
                       
        #print "sleeping..."
        # this can be a float for sub-second sleep    
        time.sleep(0.1)		# 0.1 
                              
                 