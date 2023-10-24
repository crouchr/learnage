import time,re
import PreludeEasy
import syslog
import ipintellib
import kojoney_idmef_common
import kojoney_cymru_hash

# Events for files extracted from URLs, e.g. kippo dialogue 
def sendFiledownloadIDMEF(url,fullFilename,filename,fileMD5,completion,logEntry):
    try:
        if fileMD5 != None:
            cymruHash = kojoney_cymru_hash.cymruHash(fileMD5)
            print "cymruHash : "  + cymruHash
        else:
            cymruHash = "0"
        
        # Extract IP from URL
        domain = kojoney_idmef_common.extractDomain(url)
        if domain != None :
            a = re.findall("(\d+\.\d+\.\d+\.\d+)",domain)
            if len(a) > 0 :
                dstIP = domain
            else:
                dnsInfo = ipintellib.ip2name(domain)
                dstIP = dnsInfo['name']
        else:
            dstIP = "0.0.0.0"  
        print "kojoney_anubis_idmef.py : sendFiledownloadIDMEF() : dstIP = " + dstIP.__str__()         
        
        # Create a new Prelude client
        client = PreludeEasy.ClientEasy("blackrain")
        client.Start()
                            
        # Create the IDMEF message
        idmef = PreludeEasy.IDMEF()
                                            
        # Sensor
        fieldsSet = kojoney_idmef_common.setIDMEFcommon(idmef,"Analyst Honeypot","02DEBE56",None,dstIP,None,dstIP,logEntry)
                                                            
        # Classification
        if cymruHash == "0" :
            cymruHash = "None"
            idmef.Set("alert.classification.text","File identified by URL-snarf method")
            idmef.Set("alert.assessment.impact.severity", "low")
        else:
            idmef.Set("alert.classification.text","Malware file identified by URL-snarf method" + " contains malware")
            idmef.Set("alert.assessment.impact.severity", "high")
                
        idmef.Set("alert.target(0).node.address(0).address", dstIP)
            
        idmef.Set("alert.target(0).file(0).name", filename)
        idmef.Set("alert.target(0).file(0).path", fullFilename)
                    
        # Assessment
        idmef.Set("alert.assessment.impact.completion", completion)
        if completion == "succeeded" :
            idmef.Set("alert.assessment.impact.description", "File downloaded OK")
        else:
            idmef.Set("alert.assessment.impact.description", "File download failed")
      
        idmef.Set("alert.assessment.impact.type", "file")
        
        if url == '/':
            url = "None"
        idmef.Set("alert.target(0).service.web_service.url", url)
        
        
         # Additional Data
        fieldsOffset = fieldsSet
        #print "fieldsOffset = " + fieldsOffset.__str__() 
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "Team Cymru MHA % of AV triggered")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", cymruHash)                        
        fieldsOffset = fieldsOffset + 1
        
        if fileMD5 != None:
            idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
            idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "MD5")
            idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", fileMD5)                        
                                                                                                                                     
        client.SendIDMEF(idmef)
        return
                        
    except Exception,e:
        msg = "kojoney_anubis_idmef.py : sendFiledownloadIDMEF() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return

# Events for PHP files juiced 
def botjuicePHPIDMEF(fullFilename,logEntry):
    try:
        
        logEntry = logEntry.split("BOTJUICER=")[1]
        
        # Create a new Prelude client
        client = PreludeEasy.ClientEasy("blackrain")
        client.Start()
                            
        # Create the IDMEF message
        idmef = PreludeEasy.IDMEF()
                                            
        # Sensor
        fieldsSet = kojoney_idmef_common.setIDMEFcommon(idmef,"Analyst Honeypot","02DEBE56",None,None,None,None,logEntry)
                                                            
        # Classification
        if "Undetermined" in logEntry:
            idmef.Set("alert.classification.text","PHP file - no bot identified")
            idmef.Set("alert.assessment.impact.severity", "low")
            idmef.Set("alert.assessment.impact.description", "PHP file not found to contain bot code")
        else:
            idmef.Set("alert.classification.text","PHP file - bot code identified")
            idmef.Set("alert.assessment.impact.severity", "high")
            idmef.Set("alert.assessment.impact.description", "PHP file found to contain bot code")
        
        #idmef.Set("alert.target(0).file(0).name", fullFilename)
        idmef.Set("alert.target(0).file(0).path", fullFilename)
                    
        # Assessment
        #idmef.Set("alert.assessment.impact.description", "PHP file contains bot code")
        idmef.Set("alert.assessment.impact.type", "file")
        
        # Additional Data
        #fieldsOffset = fieldsSet
        #print "fieldsOffset = " + fieldsOffset.__str__() 
        #idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        #idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "Team Cymru MHA % of AV triggered")
        #idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", cymruHash)                        
        #fieldsOffset = fieldsOffset + 1
        
        #if fileMD5 != None:
        #    idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        #    idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "MD5")
        #    idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", fileMD5)                        
                                                                                                                                     
        client.SendIDMEF(idmef)
        return
                        
    except Exception,e:
        msg = "kojoney_anubis_idmef.py : sendFiledownloadIDMEF() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return

#  
def tracerouteIDMEF(dstIP,logEntry):
    try:
        
        # Create a new Prelude client
        client = PreludeEasy.ClientEasy("blackrain")
        client.Start()
                            
        # Create the IDMEF message
        idmef = PreludeEasy.IDMEF()
                                            
        # Sensor
        fieldsSet = kojoney_idmef_common.setIDMEFcommon(idmef,"Analyst Honeypot","02DEBE56",None,dstIP,None,dstIP,"None")
                                                            
        # Classification
        idmef.Set("alert.assessment.impact.severity", "info")
        idmef.Set("alert.classification.text","Traceroute to attacker")
                        
        idmef.Set("alert.target(0).node.address(0).address", dstIP)
                        
        # Assessment
        idmef.Set("alert.assessment.impact.description", "Traceroute from honeypot to attacker IP")
        idmef.Set("alert.assessment.impact.type", "recon")
        
        # Additional Data
        logEntry = logEntry.split("TRACEROUTE : ")[1]
        
        fieldsOffset = fieldsSet
        #print "fieldsOffset = " + fieldsOffset.__str__() 
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "AS Path to attacker")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", logEntry)                        
        fieldsOffset = fieldsOffset + 1
                                                                                                                                     
        client.SendIDMEF(idmef)
        return
                        
    except Exception,e:
        msg = "kojoney_anubis_idmef.py : tracerouteIDMEF() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return

def nmapIDMEF(dstIP,logEntry):
    try:
        
        # Create a new Prelude client
        client = PreludeEasy.ClientEasy("blackrain")
        client.Start()
                            
        # Create the IDMEF message
        idmef = PreludeEasy.IDMEF()
                                            
        # Sensor
        fieldsSet = kojoney_idmef_common.setIDMEFcommon(idmef,"Analyst Honeypot","02DEBE56",None,dstIP,None,dstIP,"None")
        
        logEntry = logEntry.split("NMAP ")[1]
        if "open={}" not in logEntry:	# Attacker has open ports
            idmef.Set("alert.classification.text","Nmap against attacker - port(s) open")
        else:
            idmef.Set("alert.classification.text","Nmap against attacker - port(s) closed")
        
        # Classification
        idmef.Set("alert.assessment.impact.severity", "info")
        
        # Target                        
        idmef.Set("alert.target(0).node.address(0).address", dstIP)
                        
        # Assessment
        idmef.Set("alert.assessment.impact.description", "Nmap from honeypot to attacker IP")
        idmef.Set("alert.assessment.impact.type", "recon")
        
        # Additional Data
        fieldsOffset = fieldsSet
        #print "fieldsOffset = " + fieldsOffset.__str__() 
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "Open ports")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", logEntry)                        
        fieldsOffset = fieldsOffset + 1
                                                                                                                                     
        client.SendIDMEF(idmef)
        return
                        
    except Exception,e:
        msg = "kojoney_anubis_idmef.py : nmapIDMEF() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return
                                                                     