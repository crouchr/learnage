import time
import PreludeEasy
import syslog
import kojoney_idmef_common

def exploitIDMEF(srcIP,srcPort,dstIP,dstPort,vulnerability,vulninfo,shellcode,line):
    try:
        
        # Create a new Prelude client.
        #client = PreludeEasy.ClientEasy("honeytweeter")
        client = PreludeEasy.ClientEasy("blackrain")
        client.Start()

        # Create the IDMEF message
        idmef = PreludeEasy.IDMEF()

        # Sensor
        fieldsSet = kojoney_idmef_common.setIDMEFcommon(idmef,"Win32 Honeypot","02DEBE56",srcIP,dstIP,dstPort,srcIP,line)
                
        # Classification
        idmef.Set("alert.classification.text","Exploit using " + vulnerability + " vulnerability")
            
        if shellcode != "None" :
            #idmef.Set("alert.classification.text","Exploit using vulnerability " + vulnerability + ", shellcode decoded")
            idmef.Set("alert.assessment.impact.severity", "high")
            idmef.Set("alert.assessment.impact.completion", "succeeded")
            idmef.Set("alert.assessment.impact.description", "Win32 exploit detected against honeypot - shellcode found")
        
        else:
            #idmef.Set("alert.classification.text","Exploit using vulnerability " + vulnerability)
            idmef.Set("alert.assessment.impact.severity", "low")
            idmef.Set("alert.assessment.impact.completion", "failed")
            idmef.Set("alert.assessment.impact.description", "Win32 exploit detected against honeypot - no shellcode found")
            
        # Source
        idmef.Set("alert.source(0).node.address(0).address", srcIP)
        idmef.Set("alert.source(0).service.ip_version", 4)
        idmef.Set("alert.source(0).service.port", srcPort)
        
        # Target(s)
        idmef.Set("alert.target(0).node.address(0).address", dstIP)
        idmef.Set("alert.target(0).service.ip_version", 4)
        idmef.Set("alert.target(0).service.port", dstPort)
        
        # Assessment
        idmef.Set("alert.assessment.impact.type", "other")
        
        # Additional Data
        fieldsOffset = fieldsSet
        print "fieldsOffset = " + fieldsOffset.__str__() 
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "Shellcode")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", shellcode)
        
        fieldsOffset = fieldsOffset + 1
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "Call-back URL")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", vulninfo)
                                        
        client.SendIDMEF(idmef)
        return

    except Exception,e:
        msg = "kojoney_amun_idmef.py : exploitIDMEF() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return

# srcIP = honeypot IP
def exploitDropsiteIDMEF(srcIP,dstIP,attackerIP,dropsite,line):
    try:
        #print "exploitDropsiteIDMEF() : srcIP      : " + srcIP
        #print "exploitDropsiteIDMEF() : dstIP      : " + dstIP
        #print "exploitDropsiteIDMEF() : attackerIP : " + attackerIP
        #print "exploitDropsiteIDMEF() : dropsite   : " + dropsite
         
        # Create a new Prelude client
        client = PreludeEasy.ClientEasy("blackrain")
        client.Start()

        # Create the IDMEF message
        idmef = PreludeEasy.IDMEF()

        # Sensor
        fieldsSet = kojoney_idmef_common.setIDMEFcommon(idmef,"Win32 Honeypot","02DEBE56",srcIP,dstIP,None,dstIP,line)
                
        # Classification
        if dstIP == attackerIP :	# see Jose Nazario "Internet Worms", page 100 figure 6.2
            idmef.Set("alert.classification.text","Malware download requested from parent")
        else:
            idmef.Set("alert.classification.text","Malware dropsite extracted from shellcode")
            
        #idmef.Set("alert.classification.text","Exploit using vulnerability " + vulnerability + ", shellcode decoded")
        idmef.Set("alert.assessment.impact.severity", "info")
        #idmef.Set("alert.assessment.impact.completion", "succeeded")
        idmef.Set("alert.assessment.impact.description", "Malware propagation method determined")
            
        # Source - the honeypot
        idmef.Set("alert.source(0).node.address(0).address", srcIP)
        idmef.Set("alert.source(0).service.ip_version", 4)
        #idmef.Set("alert.source(0).service.port", srcPort)
        
        # Target(s)
        idmef.Set("alert.target(0).node.address(0).address", dstIP)
        idmef.Set("alert.target(0).service.ip_version", 4)
        #idmef.Set("alert.target(0).service.port", dstPort)
        
        # Assessment
        idmef.Set("alert.assessment.impact.type", "other")
        
        # Additional Data
        #fieldsOffset = fieldsSet
        #print "fieldsOffset = " + fieldsOffset.__str__() 
        #idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        #idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "Shellcode")
        #idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", shellcode)
        
        #fieldsOffset = fieldsOffset + 1
        #idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        #idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "Call-back URL")
        #idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", vulninfo)
                                        
        client.SendIDMEF(idmef)
        return

    except Exception,e:
        msg = "kojoney_amun_idmef.py : exploitDropsiteIDMEF() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return
        
if __name__ == '__main__' :
    exploitIDMEF("6.6.6.6","34","192.168.1.64","445","SYMANTEC","callback_url","leimbach","Here is line from log")

    #portScanIDMEF("7.7.7.7","TCP scan","22","Here is line from log")
    #time.sleep(1)
    #portScanIDMEF("7.7.7.7","UDP scan","53","Here is line from log")
    #time.sleep(1)
    #portScanIDMEF("7.7.7.7","SYN scan","25","Here is line from log")
    #time.sleep(1)
    
    