#!/usr/bin/python

import os,sys,syslog

# sid is a string
# msg:"ET WEBSERVER Poison Null Byte"; 
# bug : need to use regex to handle cases where text contains ":" e.g. 2008974
#def getSnortMsg(sid):
#    try:
#        cmd = 'grep \"sid:[ ]*' + sid + ';\" /home/snort/rules/*.rules'
#        #print "cmd is {" + cmd + "}"
#        pipe = os.popen(cmd,'r')
#    
#        line = pipe.read()
#    
#        start = line.find("msg:")
#    
#        if start != -1 : # we have found "msg:"
#            #msgText=line[start:].split(":")[1]
#            msgText=line[start:]
#            msgText=msgText.split(";")[0]
#            msgText=msgText[4:]			# lose the "msg=" part
#            msgText=msgText.replace(","," ")	# replace commas with space -> i.e. if message needs to go nto .csv file	
#            #msgText=msgText.strip('"')
#            #print msgText   
#        else:
#            return "?"			# can't find     
#    
#        result = msgText
#        #result = result.split('"')[1]
#    
#        #print "result=" + msgText 
#        return result
#    
#    except Exception,e:
#            syslog.syslog("getSnortInfo.py : getSnortMsg() exception caught = " + `e` + "line=" + line)
#            return "!"        
#
#
#

#line = 'Jan  5 15:11:58 mars psad: src: 195.171.3.69 signature match: "SHELLCODE x86 inc ebx NOOP" (sid: 1390) tcp port: 445 FWSNORT_INPUT rule: 682'
#[2010-05-09 01:15:40 Host:172.31.0.67 UID:0 PID:4252 CMD:sshd]:cmd=SSH-2.0-libssh-0.1

# snort sid
#pat = "\[[0-9]:([0-9]*):[0-9]*"


# psad
#pat = "signature match: \"([A-Za-z0-9 ]*)\""
#a = re.findall(pat,line)
#print "signature is " + a[0]


# ------------------------

# Extract interesting data from all sebek entries
def filterSebek(line):

    try:
        print "filterSebek() : entered with line:" + line 
        linec=line 	# make a copy of line
    
        line=line.split(":")
        process = line[6].rstrip("]")
    
        line=linec
        line=line.split("=")
        cmd = line[1]
    
        sebek = "process=" + process + " cmd=" + cmd
        print "filterSebek() : sebek = " + sebek 
    
        # filter out boring info
        if len(cmd) == 0 :
            print "filterSebek() : no cmd found : " + cmd 
            return ""
        
        # private information - non-honeypot passwords
        if cmd.find("s0lab0sch") != -1 or cmd.find("ialwtt") != -1 :
            print "filterSebek() : contains private data : " + cmd 
            return ""
    
        # SSH brute force attempts
        if cmd.find("libssh") != -1 or cmd.find("dropbear") != -1 or cmd.find("PuTTY") != -1 or cmd.find("OpenSSH") != -1 or cmd.find("SSH-2.0") != -1 :
            print "filterSebek() : brute force attempt : " + linec 
            return ""    
    
        # local access via console - i.e. me accessing - comment this out for debugging on Qemu console
        #if process.find("agetty") != -1 or process.find("login") != -1 :
        #    return ""    

        # local access via Qemu VM console - i.e. me accessing - comment this out for debugging on Qemu console
        #if process.find("bash") != -1 :
        #    return ""    
        
        # SSHD - this is some sort of summary of previous cmds already reported by sh but with missing \n so not useful
        if process.find("sshd") != -1  :
            return ""    

        # IRC ?
        if process.find("inetd") != -1 and (cmd.find("ERROR") != -1 or cmd.find("NOTICE") != -1 or cmd.find("NOTICE") != -1 or cmd.find("PING") != -1)  :
            return ""    
    
        # IRC via proxy ?
        if process.find("httpd") != -1 and (cmd.find("ERROR") != -1 or cmd.find("NOTICE") != -1 or cmd.find("NOTICE") != -1 or cmd.find("PING") != -1)  :
            return ""    

        # set fake CLI prompt based on UID
        if linec.find(" UID:0 ") != -1 :
             prompt = "#"
        else :
            prompt = "$"
        
        # now filter out the Host IP
        line = linec
        line = line.split(" ")
        
        # note use of {} sp that keystrokes enclosed in [] can be distinguished
        print "filterSebek() : line = " + `line`
        tidyStr = line[0].lstrip("[") + " " + line[1] + " " + line[3] + " " + line[4] + " " + "{" + process + "}" + " " + prompt + " " + cmd
    
        print "filterSebek() : tidyStr = " + tidyStr
        return tidyStr
    
    except Exception,e:
        syslog.syslog("filter_sebek.py : filterSebek() exception caught = " + `e` + "line=" + line)
        return "!"        
#
#   


 
#fpIn = open('/home/var/log/sebek.log.txt')
#while True:
#    line = fpIn.readline().strip('\n')
#    if not line: break
#    sebek = filterSebek(line)
#    if len(sebek) > 0 :
#        print sebek

