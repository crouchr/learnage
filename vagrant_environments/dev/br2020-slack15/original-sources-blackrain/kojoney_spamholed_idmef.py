import PreludeEasy
import time
import kojoney_idmef_common

def sendSpamholedIDMEF(srcIP,dstIP,dstPort,text,count,passthrough,logEntry):
    try:
        attackerIP = srcIP
        # Create a new Prelude client.
        client = PreludeEasy.ClientEasy("blackrain")
        client.Start()

        # Create the IDMEF message
        idmef = PreludeEasy.IDMEF()
        
        # Sensor 
        fieldsSet = kojoney_idmef_common.setIDMEFcommon(idmef,"Honeypot","02DEBE56",srcIP,dstIP,dstPort,attackerIP,logEntry)
         
        # Classification
        idmef.Set("alert.classification.text",text)

        # Source
        idmef.Set("alert.source(0).node.address(0).address", srcIP)
        
        # Target(s)
        idmef.Set("alert.target(0).node.address(0).address", dstIP)
        idmef.Set("alert.target(0).service.port", dstPort)
        
        # Service info
        idmef.Set("alert.target(0).service.iana_protocol_name", "tcp")
        idmef.Set("alert.target(0).service.iana_protocol_number", 6)
        idmef.Set("alert.target(0).service.ip_version", 4)

        idmef.Set("alert.source(0).process.name","spamhole")
                    
        # Assessment
        idmef.Set("alert.assessment.impact.severity", "medium")
        if passthrough == True:
            idmef.Set("alert.assessment.impact.completion", "succeeded")
            idmef.Set("alert.assessment.impact.severity", "medium")	# we are allowing a SPAM through
            idmef.Set("alert.assessment.impact.description", "Spammer connected with SMTP Honeypot - probe mails permitted")
        else:
            idmef.Set("alert.assessment.impact.completion", "failed")
            idmef.Set("alert.assessment.impact.severity", "low")
            idmef.Set("alert.assessment.impact.description", "Spammer connected with SMTP Honeypot - probe mails blocked")
            
        # Additional Data
        fieldsOffset = fieldsSet
        print "fieldsOffset = " + fieldsOffset.__str__()
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "connection count")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", count)
        
        #idmef.Set("alert.additional_data(0).type", "string")
        #idmef.Set("alert.additional_data(0).meaning", "connection count")
        #idmef.Set("alert.additional_data(0).data", count)
                                       
        result = client.SendIDMEF(idmef)
        #print result.__str__()
        return
        
    except Exception,e:
        print "Exception : " + e.__str__()
        return

def sendSpamholedEhloIDMEF(srcIP,dstIP,dstPort,text,ehloStr,logEntry):
    try:
        # Create a new Prelude client.
        client = PreludeEasy.ClientEasy("blackrain")
        client.Start()

        # Create the IDMEF message
        idmef = PreludeEasy.IDMEF()

        fieldsSet = kojoney_idmef_common.setIDMEFcommon(idmef,"Honeypot","02DEBE56",srcIP,dstIP,dstPort,attackerIP,logEntry)
        
        # Classification
        idmef.Set("alert.classification.text",text)

        # Source
        idmef.Set("alert.source(0).node.address(0).address", srcIP)
        
        # Target(s)
        idmef.Set("alert.target(0).node.address(0).address", dstIP)
        idmef.Set("alert.target(0).service.port", dstPort)
        
        # Service info
        idmef.Set("alert.target(0).service.iana_protocol_name", "tcp")
        idmef.Set("alert.target(0).service.iana_protocol_number", 6)
        idmef.Set("alert.target(0).service.ip_version", 4)

        idmef.Set("alert.source(0).process.name","spamhole")
                    
        # Assessment
        idmef.Set("alert.assessment.impact.completion", "succeeded")
        idmef.Set("alert.assessment.impact.severity", "medium")	
        idmef.Set("alert.assessment.impact.description", text)
        
            
        # Additional Data
        #idmef.Set("alert.additional_data(0).type", "string")
        #idmef.Set("alert.additional_data(0).meaning", "HELO/EHLO sent by spammer")
        #idmef.Set("alert.additional_data(0).data", ehloStr)
        
        fieldsOffset = fieldsSet
        print "fieldsOffset = " + fieldsOffset.__str__()
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "HELO/EHLO sent by Spammer")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", ehloStr)
                                       
        result = client.SendIDMEF(idmef)
        #print result.__str__()
        return
        
    except Exception,e:
        print "Exception : " + e.__str__()
        return

def sendSpamholedMailfromIDMEF(srcIP,dstIP,dstPort,text,spammerEmail,logEntry):
    try:
        attackerIP = srcIP
        
        # Create a new Prelude client.
        client = PreludeEasy.ClientEasy("blackrain")
        client.Start()

        # Create the IDMEF message
        idmef = PreludeEasy.IDMEF()
 
        # Sensor                   
        fieldsSet = kojoney_idmef_common.setIDMEFcommon(idmef,"Honeypot","02DEBE56",srcIP,dstIP,dstPort,attackerIP,logEntry)
         
        # Classification
        idmef.Set("alert.classification.text",text)

        # Source
        idmef.Set("alert.source(0).node.address(0).address", srcIP)
        
        # Target(s)
        idmef.Set("alert.target(0).node.address(0).address", dstIP)
        idmef.Set("alert.target(0).service.port", dstPort)
        
        # Service info
        idmef.Set("alert.target(0).service.iana_protocol_name", "tcp")
        idmef.Set("alert.target(0).service.iana_protocol_number", 6)
        idmef.Set("alert.target(0).service.ip_version", 4)

        idmef.Set("alert.source(0).process.name","spamhole")
                    
        # Assessment
        idmef.Set("alert.assessment.impact.completion", "succeeded")
        idmef.Set("alert.assessment.impact.severity", "medium")	
        idmef.Set("alert.assessment.impact.description", text)
        
        # Additional Data
        #idmef.Set("alert.additional_data(0).type", "string")
        #idmef.Set("alert.additional_data(0).meaning", "Spammer email address")
        #idmef.Set("alert.additional_data(0).data", spammerEmail)
        
        fieldsOffset = fieldsSet
        print "fieldsOffset = " + fieldsOffset.__str__()
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "Spammer email address")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", spammerEmail)                               
        
        result = client.SendIDMEF(idmef)
        #print result.__str__()
        return
        
    except Exception,e:
        print "Exception : " + e.__str__()
        return
        
if __name__ == '__main__' :
    sendSpamholedIDMEF("2.2.2.2","192.168.1.61","10025","Spam probe SMTP session","45",True,"This is a test log entry")
    sendSpamholedIDMEF("2.2.2.2","192.168.1.61","10025","Spam probe SMTP session","45",False,"This is a test log entry")
    sendSpamholedEhloIDMEF("2.2.2.2","192.168.1.61","10025","Spammer said EHLO","test@test.com","This is a test log entry")
    sendSpamholedMailfromIDMEF("2.2.2.2","192.168.1.61","10025","Spammer said MAIL:FROM","spammer@spammer.com","This is a test log entry")
 