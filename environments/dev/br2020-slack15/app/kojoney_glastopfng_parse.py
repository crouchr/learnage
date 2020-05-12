#!/usr/bin/python

import time, os , syslog , re 
import kojoney_funcs
import kojoney_afterglow
import ipintellib

#2010-09-27 18:49:01,487 INFO [submit_md5] download (http://208.53.183.171:80/h.exe): 748610496089bcb82b95fe67062f314c (size: 94208) - MS08067
#2010-09-27 18:49:07,532 INFO [submit_anubis] anubis result: http://anubis.iseclab.org/?action=result&task_id=1e285a7544512cd4439e2fcbc0d52c2e7
# return the Tweet or None

def processGlastopf(line):
    
    asMsg = ""
    
    try :
        #print "processGlastopf() : line read is " + line

        # Successful attack
        if line.find("attack from") != -1 or line.find("Mail attack found from") != -1 :
            fields = line.split(" - ")
            #print fields
            msg = ' '.join(fields[3:])
            #msg = ' '.join(fields[3:]).rstrip("?")		# does glastopf add trailing ? / ??
            msg = "WEB_X," + msg
            msg = msg.replace(" with request: "," req=")
            msg = msg.replace("found from","from")		# normalise MAIL versus "other" attacks
            msg = msg.replace("Mail","Webmail")			# normalise MAIL versus "other" attacks
            return msg

        # File retrieved
        if line.find("successfully opened") != -1 :
            fields = line.split(" - ")
            #print fields
            msg = ' '.join(fields[3:])
            msg = "WEB_OPEN," + msg
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
            return msg

        # Scan - i.e. unsuccessful attack
        if line.find("No attack found") != -1 :
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
            else:				# LOC = local
                msg = msg.replace("No attack found from","WEB_SCN,Scan from")
            msg = msg.replace(" with request: "," req=")
            msg = msg.rstrip();	# remove any trailing characters
            #msg = msg + " ISP=" + asMsg
            kojoney_afterglow.visWebScan(msg)
            return msg
                    
        return None

    except Exception,e:
                syslog.syslog("kojoney_glastopf_parse.py : processGlastopf() : " + `e` + " line=" + line)

                               
# -------------------------------------------------------
        
# Start of code
# This is a test harness so comment/uncomment the relevent lines        
        
if __name__ == '__main__' :
       
# Set the input file to scan
    filename = '/usr/local/src/glastopf/log/glastopf.log'
    file = open(filename,'r')

    while True:
    
        # Tweets log file       
        # where = file.tell()
        line  = file.readline()
        line  = line.rstrip('\n')
        
        if not line:		# no data to process
            pass
        else :			# new data has been found
            msg = processGlastopf(line)
            
        if msg != None:
            print "*** Tweet : " + msg
                       
        #print "sleeping..."
        # this can be a float for sub-second sleep    
        time.sleep(0)		# 0.1 
                              
                 