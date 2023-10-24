#!/usr/bin/python

import time, os , syslog , re 
import PreludeEasy
#import kojoney_amun_idmef
import kojoney_idmef_common
import virustotal
#import ipintellib


# copied from kojoney_anubis.py
def calcMD5(fullFilename):
    try:
        cmd = "/usr/bin/md5sum " + fullFilename.__str__()
        pipe = os.popen(cmd,'r')
        raw = pipe.read().rstrip("\n")
        #print raw
        result = raw.split(" ")[0]
                               
        if "No such file" in raw :
            print "calcMD5() : No such file : " + fullFilename.__str__()
            return None
        else:
            return result
                                                                                           
    except Exception,e:
        msg = "kojoney_anubis.py : calcMD5() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return None
                                                                                                                                            

# /usr/local/maldetect/event_log
#Feb 07 18:50:47 mars maldet(27517): {mon} inotify file scan /tmp/192.168.1.74:4690-192.168.1.67:60064
#Feb 07 18:50:47 mars maldet(27517): {mon} inotify file scan /tmp/38.229.0.51:43-192.168.1.67:48053
#Feb 07 18:50:47 mars maldet(27517): {mon} inotify file scan /tmp/d1e.txt
#Feb 07 18:50:48 mars maldet(27517): {hexstring} malware hit {HEX}perl.ircbot.Arabhack.55 on /tmp/d1e.txt
#Feb 07 18:50:48 mars maldet(27517): {mon} inotify file scan /tmp/processTable.txt
#Feb 07 18:50:48 mars maldet(27517): {mon} inotify file scan /tmp/routeTable.txt
#Feb 07 18:50:48 mars maldet(27517): {mon} inotify file scan /tmp/test_clamd.sh
# return the Tweet or None
                
# return the Tweet or None
def processMaldet(txnId,sensorId,line):
    
    try:
        #print "processAmunDownload() : line read is " + line
        line = line.rstrip()
        
        if "malware hit " not in line :
            return None
        
        print "----------------------------------"
        #line = line.replace(" on "," file=")
               
        fields = line.split("malware hit ")
        print "processMaldet() : fields = " + fields.__str__()
        
        msg = fields[1]
        print "processMaldet() : msg = " + msg
        signature = msg.split(" ")[0]
                
        filepath = msg.split("on ")[1]
        filename = filepath.split("/")[-1]
        print "processMaldet() : filepath  = " + filepath.__str__()
        print "processMaldet() : filename  = " + filename.__str__()
        print "processMaldet() : signature = " + signature.__str__()

        # filename will have flow info if cl_sniffer captured it
        ips = re.findall("(\d+\.\d+\.\d+\.\d+):(\d+)\-(\d+\.\d+\.\d+\.\d+):(\d+)",line)
        if len(ips) > 0 :
            flowInfo = "Flow information found in filename : " + ips.__str__()
            srcIP   = ips[0][0]
            srcPort = ips[0][1]
            dstIP   = ips[0][2]
            dstPort = ips[0][3]
            flowInfo = " " + srcIP + " ports={" + srcPort + " " + dstPort + "}"                                                        
        else:
            flowInfo = " "
            
        #print "filepath=[" + filepath + "]"
        malwareMD5 = calcMD5(filepath)
        if len(malwareMD5) <= 0:
            malwareMD5 = "ERROR"

        signature = signature.replace("{HEX}","")    
            
        msg = "LMD," + signature + flowInfo + " MD5=" + malwareMD5 + " file=" + filepath.__str__()
        
        #print "md5 : " + malwareMD5.__str__()
        #if malwareMD5 != None :
        #    result = virustotal.getVirusTotalFile(malwareMD5,"ALL",False)
        #
        #    if result['status'] == True:
        #        signature = result['single']
        #        bitly     = result['bitly']
        #    else:
        #        signature = "NO_SIG"
        #        bitly     = ""
        #
        #    msg = msg.rstrip(" ")      
        #    msg = "LMD-MALDETECT," + msg + " MD5=" + malwareMD5 + " -> " + signature + " " + result['bitly']
        #msg = "LMD-MALDETECT," + msg + " MD5=" + malwareMD5 + " -> " + signature + " " + result['bitly']      
        #    #sendMaldetIDMEF("Malware detected on Honeypot",signature,filepath,bitly,line)
        #else:
        #    print msg
            
        return msg

    except Exception,e:
        msg = "kojoney_maldet_parse.py : processMaldet() : exception : " + e.__str__() + " line=" + line
        print msg
        syslog.syslog(msg)
         
def sendMaldetIDMEF(attackType,signature,filepath,bitly,logEntry):
    try:        
        # Create a new Prelude client.
        client = PreludeEasy.ClientEasy("blackrain")
        client.Start()
                                                            
        # Create the IDMEF message
        idmef = PreludeEasy.IDMEF()
                                                                            
        # Sensor
        fieldsSet = kojoney_idmef_common.setIDMEFcommon(idmef,"Honeypot","02DEBE56",None,None,None,None,logEntry)
                                                                                            
        # Classification
        idmef.Set("alert.classification.text",attackType)
        idmef.Set("alert.assessment.impact.severity", "high")
        idmef.Set("alert.assessment.impact.description", "Malware detected on Honeypot")
                                                                                                                                
        # Target(s) 
        #idmef.Set("alert.target(0).file(0).name", fileMD5)
        idmef.Set("alert.target(0).file(0).path", filepath)
        
        # Assessment
        idmef.Set("alert.assessment.impact.completion", "succeeded")
        idmef.Set("alert.assessment.impact.type", "file")
                                                                                                                                                                                                                   # Additional Data
        fieldsOffset = fieldsSet
        #print "fieldsOffset = " + fieldsOffset.__str__() 
        #idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        #idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "Team Cymru MHA % of AV triggered")
        #idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", cymruHash)
        
        client.SendIDMEF(idmef)      
                                                                                                                                                                                                                                              
    except Exception,e:
        msg = "sendMaldetIDMEF() : exception : " + e.__str__()    
        print msg
        syslog.syslog(msg)
                                                                                                                                                                                                                                                            
# Start of code
# This is a test harness so comment/uncomment the relevent lines        
        
if __name__ == '__main__' :
       
# Set the input file to scan
    filename = '/usr/local/maldetect/event_log'
    file = open(filename,'r')

    while True:
        line  = file.readline()
        line = line.rstrip('\n')
        
        if not line:		# no data to process
            pass
        else :			# new data has been found
            
            msg = processMaldet(123,"TEST",line)
        
        if msg != None:
            print "*** msg after parsing = [" + msg +"]"
                       
        #print "sleeping..."
        # this can be a float for sub-second sleep    
        #time.sleep(0.01)		# 0.1 
                              
        