import time
import PreludeEasy
import syslog
import ipintellib
import kojoney_idmef_common
import kojoney_cymru_hash

# Web-based RFI attacks
def sendWebAppIDMEF(attackType,url,service,dstPort,completion,srcIP,dstIP,apacheCLF,attackerIP,line):
    try:
        
        # Create a new Prelude client.
        client = PreludeEasy.ClientEasy("blackrain")
        client.Start()

        # Create the IDMEF message
        idmef = PreludeEasy.IDMEF()

        # Sensor
        fieldsSet = kojoney_idmef_common.setIDMEFcommon(idmef,"Web Honeypot","02DEBE56",srcIP,dstIP,dstPort,attackerIP,line)
        
        # Classification
        idmef.Set("alert.classification.text",attackType)
    
        # Source
        idmef.Set("alert.source(0).node.address(0).address", srcIP)
        idmef.Set("alert.source(0).service.iana_protocol_name", "tcp")  
        idmef.Set("alert.source(0).service.ip_version", 4)
        
        # Target(s)
        idmef.Set("alert.target(0).node.address(0).address", dstIP)
        
        # Service
        idmef.Set("alert.target(0).service.iana_protocol_name", "tcp") 
        idmef.Set("alert.target(0).service.ip_version", 4)
        idmef.Set("alert.target(0).service.name", service)
        idmef.Set("alert.target(0).service.port", dstPort)
        
        # Web Service specific details
        if "GET" in attackType:
            idmef.Set("alert.target(0).service.web_service.http_method", "GET")
        elif "POST" in attackType:
            idmef.Set("alert.target(0).service.web_service.http_method", "POST")
        
        idmef.Set("alert.target(0).service.web_service.url", url)
        
        cgi,arg = kojoney_idmef_common.extractCGI(url)
        if cgi != None:
            idmef.Set("alert.target(0).service.web_service.cgi", cgi)
        if arg != None:
            idmef.Set("alert.target(0).service.web_service.arg", arg)
        
        # Assessment    
        idmef.Set("alert.assessment.impact.type", "other")
        idmef.Set("alert.assessment.impact.completion", completion)
        if completion == "succeeded" :
            idmef.Set("alert.assessment.impact.severity", "high")
        else:
            idmef.Set("alert.assessment.impact.severity", "low")
        
        idmef.Set("alert.assessment.impact.description", "Attempted Web Application Remote File Inclusion (RFI) attack")
        
        # Additional Data
        fieldsOffset = fieldsSet
        print "fieldsOffset = " + fieldsOffset.__str__() 
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "Apache CLF Record")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", apacheCLF)
        
        client.SendIDMEF(idmef)
        return

    except Exception,e:
        msg = "kojoney_glastopf_idmef.py : sendWebAppIDMEF() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return

def sendWebAppURLIDMEF(attackType,url,dstService,srcIP,dstIP,dstPort,completion,apacheCLF,attackerIP,logEntry):
    try:
        print "sendWebAppURLIDMEF() : srcIP      : " + srcIP
        print "sendWebAppURLIDMEF() : dstIP      : " + dstIP
        print "sendWebAppURLIDMEF() : apacheCLF  : " + apacheCLF
        print "sendWebAppURLIDMEF() : attackerIP : " + attackerIP
        print "sendWebAppURLIDMEF() : url        : " + url
                
        # Create a new Prelude client.
        client = PreludeEasy.ClientEasy("blackrain")
        client.Start()

        # Create the IDMEF message
        idmef = PreludeEasy.IDMEF()
        
        # Sensor
        fieldsSet = kojoney_idmef_common.setIDMEFcommon(idmef,"Web Honeypot","02DEBE56",srcIP,dstIP,dstPort,attackerIP,logEntry)
        
        # Classification
        idmef.Set("alert.classification.text",attackType)

        idmef.Set("alert.target(0).service.iana_protocol_name", "tcp")
        idmef.Set("alert.target(0).service.ip_version", 4)
        idmef.Set("alert.target(0).service.name", dstService)	# bug : is this working ?
            
        # Source - no info in the Glastopf log so need to construct it
        idmef.Set("alert.source(0).node.address(0).address", srcIP)
        idmef.Set("alert.source(0).service.iana_protocol_name", "tcp")
        idmef.Set("alert.source(0).service.ip_version", 4)
        
        # Target(s)
        idmef.Set("alert.target(0).node.address(0).address", dstIP)
        idmef.Set("alert.target(0).service.iana_protocol_name", "tcp")
        idmef.Set("alert.target(0).service.port", dstPort)
        if url == '/':
            url = "None"
        idmef.Set("alert.target(0).service.web_service.url", url)
        
        # Assessment
        idmef.Set("alert.assessment.impact.severity", "medium")
        idmef.Set("alert.assessment.impact.completion", completion)
        idmef.Set("alert.assessment.impact.type", "file")
        idmef.Set("alert.assessment.impact.description", "Web URL request")
        
        # Additional Data
        fieldsOffset = fieldsSet
        print "fieldsOffset = " + fieldsOffset.__str__() 
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "Apache CLF Record")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", apacheCLF)
          
        client.SendIDMEF(idmef)
        return

    except Exception,e:
        msg = "kojoney_glastopf_idmef.py : sendWebAppURLIDMEF() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return

def sendWebAppFile(attackType,fileMD5,logEntry):
    try:        
        cymruHash = kojoney_cymru_hash.cymruHash(fileMD5)
        print "cymruHash : "  + cymruHash
                
        # Create a new Prelude client.
        client = PreludeEasy.ClientEasy("blackrain")
        client.Start()

        # Create the IDMEF message
        idmef = PreludeEasy.IDMEF()
        
        # Sensor
        fieldsSet = kojoney_idmef_common.setIDMEFcommon(idmef,"Web Honeypot","02DEBE56",None,None,None,None,logEntry)
        
        # Classification
        if cymruHash == "0" :
            cymruHash = "None"
            idmef.Set("alert.classification.text",attackType)
            idmef.Set("alert.assessment.impact.severity", "low")
            idmef.Set("alert.assessment.impact.description", "File retrieved - no AV triggered")
        else:
            idmef.Set("alert.classification.text",attackType + " contains malware")
            idmef.Set("alert.assessment.impact.severity", "high")
            idmef.Set("alert.assessment.impact.description", "Malware file retrieved - at least one AV triggered")
                    
        # Target(s)
        idmef.Set("alert.target(0).node.address(0).address", "192.168.1.62")
        idmef.Set("alert.target(0).file(0).name", fileMD5)
        idmef.Set("alert.target(0).file(0).path", '/usr/local/src/glastopf/files/' + fileMD5)	# not actually true
        
        # Assessment
        idmef.Set("alert.assessment.impact.completion", "succeeded")
        idmef.Set("alert.assessment.impact.type", "file")
        
        # Additional Data
        fieldsOffset = fieldsSet
        #print "fieldsOffset = " + fieldsOffset.__str__() 
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "Team Cymru MHA % of AV triggered")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", cymruHash)
          
        client.SendIDMEF(idmef)
        return

    except Exception,e:
        msg = "kojoney_glastopf_idmef.py : sendWebAppFile() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return
        
if __name__ == '__main__' :
    sendWebAppIDMEF("GET attack","/php/phpmyadmin","http","18080","succeeded","7.7.7.7","192.168.1.62","Fake ApacheCLF record here","8.8.8.8","Fake log entry here")
    time.sleep(1)
    
    sendWebAppIDMEF("POST attack","/php/phpmyadmin","http","18080","succeeded","7.7.7.7","192.168.1.62","Fake ApacheCLF record here","8.8.8.8","Fake log entry here")
    time.sleep(1)
    
    sendWebAppIDMEF("Webmail attack","/php/phpmyadmin","http","18080","succeeded","7.7.7.7","192.168.1.62","Fake ApacheCLF record here","8.8.8.8","Fake log entry here")
    
    