#!/usr/bin/python

import os,sys,syslog

# sid is a string
# msg:"ET WEBSERVER Poison Null Byte"; 
# bug : need to use regex to handle cases where text contains ":" e.g. 2008974
def getSnortMsg(sid):
    try:
#       cmd = 'grep \"sid:' + sid + ';\" /home/snort/rules/*.rules'
        cmd = 'grep \"sid:[ ]*' + sid + ';\" /home/snort/rules/*.rules'
        #print "cmd is {" + cmd + "}"
        pipe = os.popen(cmd,'r')
    
        line = pipe.read()
    
        start = line.find("msg:")
    
        if start != -1 : # we have found "msg:"
            #msgText=line[start:].split(":")[1]
            msgText=line[start:]
            msgText=msgText.split(";")[0]
            msgText=msgText[4:]			# lose the "msg=" part
            msgText=msgText.replace(","," ")	# replace commas with space -> i.e. if message needs to go nto .csv file	
            #msgText=msgText.strip('"')
            #print msgText   
        else:
            return "?"			# can't find     
    
        result = msgText
        #result = result.split('"')[1]
    
        #print "result=" + msgText 
        return result
    
    except Exception,e:
            syslog.syslog("getSnortInfo.py : getSnortMsg() exception caught = " + `e` + "line=" + line)
            return "!"        

# sid is a string
#classtype:web-application-activity; 
def getSnortAtom(sid,keyword):
    try:
        cmd = 'grep \"sid:[ ]*' + sid + ';\" /home/snort/rules/*.rules'
        #print "cmd is [" + cmd + "]"
        pipe = os.popen(cmd,'r')
    
        line = pipe.read()
    
        start = line.find(keyword + ":")
    
        if start != -1	: # we have found "msg:"
            msgText = line[start:].split(":")[1]
            msgText = '"' + msgText.split(";")[0] + '"'
        else:
            return "?"     
            
        msgText=msgText.replace(","," ")
        result = msgText
    
        #print result
        return result
    
    except Exception,e:
            syslog.syslog("getSnortInfo.py : getSnortAtom() exception caught = " + `e` + "line=" + line)
            return "!"        

# PSAD 
######

# sid is a string
# msg:"ET WEBSERVER Poison Null Byte"; 
def getPsadMsg(sid):
    try:
        cmd = 'grep \"sid:[ ]*' + sid + ';\" /etc/psad/signatures'
        #print "cmd is [" + cmd + "]"
        pipe = os.popen(cmd,'r')
    
        line = pipe.read()
    
        start = line.find("msg:")
    
        if start != -1	: # we have found "msg:"
            msgText=line[start:].split(":")[1]
            msgText=msgText.split(";")[0]
            #msgText=msgText.strip('"')
            #print msgText   
        else:
            return "?"     
    
        result = msgText
        #result = result.split('"')[1]
    
        #print "result=" + msgText 
        return result
    
    except Exception,e:
            syslog.syslog("getSnortInfo.py : getSnortMsg() exception caught = " + `e` + "line=" + line)
            return "!"        

# sid is a string
#classtype:web-application-activity; 
def getPsadAtom(sid,keyword):
    try:
        cmd = 'grep \"sid:[]*' + sid + ';\" /etc/psad/signatures'
        #print "cmd is [" + cmd + "]"
        pipe = os.popen(cmd,'r')
    
        line = pipe.read()
    
        start = line.find(keyword + ":")
    
        if start != -1	: # we have found "msg:"
            msgText = line[start:].split(":")[1]
            msgText = '"' + msgText.split(";")[0] + '"'
        else:
            return "?"     
    
        result = msgText
    
        #print result
        return result
    
    except Exception,e:
            syslog.syslog("getSnortInfo.py : getPsadAtom() exception caught = " + `e` + "line=" + line)
            return "!"        

# FWSNORT
#########

# sid is a string
# msg:"ET WEBSERVER Poison Null Byte"; 
def getFwsnortMsg(sid):
    try:
        cmd = 'grep \"sid:[ ]*' + sid + ';\" /etc/fwsnort/snort_rules/*.rules'
        #print "cmd is [" + cmd + "]"
        pipe = os.popen(cmd,'r')
    
        line = pipe.read()
    
        start = line.find("msg:")
    
        if start != -1	: # we have found "msg:"
            msgText=line[start:].split(":")[1]
            msgText=msgText.split(";")[0]
            #msgText=msgText.strip('"')
            #print msgText   
        else:
            return "?"     
    
        result = msgText
        #result = result.split('"')[1]
    
        #print "result=" + msgText 
        return result
    
    except Exception,e:
            syslog.syslog("getSnortInfo.py : getFwsnortMsg() exception caught = " + `e` + "line=" + line)
            return "!"        

# sid is a string
#classtype:web-application-activity; 
def getFwsnortAtom(sid,keyword):
    try:
        cmd = 'grep \"sid:[ ]*' + sid + ';\" /etc/fwsnort/snort_rules/*.rules'
        #print "cmd is [" + cmd + "]"
        pipe = os.popen(cmd,'r')
    
        line = pipe.read()
    
        start = line.find(keyword + ":")
    
        if start != -1	: # we have found "msg:"
            msgText = line[start:].split(":")[1]
            msgText = '"' + msgText.split(";")[0] + '"'
        else:
            return "?"     
    
        result = msgText
    
        #print result
        return result
    
    except Exception,e:
            syslog.syslog("getSnortInfo.py : getFwsnortAtom() exception caught = " + `e` + "line=" + line)
            return "!"        


# ------------------------


#print "\nSNORT"
#sid = "2002911"
#sid = "2003099"
#sid = "100205"
#sid = "483"
#sid="2008974"
#sid="2000348"
#sid="2000345"
#print "sid        = " + `sid`
#print "msg        = " + getSnortMsg(sid) 
#print "classtype  = " + getSnortAtom(sid,"classtype")
#print "reference  = " + getSnortAtom(sid,"reference")

#print "\nPSAD"
#sid = "239"
#print "sid        = " + `sid` + " : " + getPsadMsg(sid)
#print "classtype  = " + getPsadAtom(sid,"classtype")
#print "reference  = " + getPsadAtom(sid,"reference")

#print "\nFWSNORT"
#sid = "2589"
#print "sid        = " + `sid` + " : " + getFwsnortMsg(sid)
#print "classtype  = " + getFwsnortAtom(sid,"classtype")
#print "reference  = " + getFwsnortAtom(sid,"reference")

#print " "

# add trailing ;
# error handling for if can't find the match 
# add todo : prioritise cve references

