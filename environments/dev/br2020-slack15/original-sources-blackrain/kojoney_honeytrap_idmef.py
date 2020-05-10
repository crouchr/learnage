#!/usr/bin/python

import PreludeEasy
import kojoney_idmef_common

def sendHoneytrapIDMEF(srcIP,dstIP,dstPort,p0f,logEntry):
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
        idmef.Set( "alert.classification.text", "Inbound TCP connection to Honeytrap daemon")

        # Source
        idmef.Set("alert.source(0).node.address(0).address", srcIP)
        
        # Target(s)
        idmef.Set("alert.target(0).node.address(0).address", dstIP)
        idmef.Set("alert.target(0).service.port", dstPort)
        
        idmef.Set("alert.target(0).service.iana_protocol_name", "tcp")
        idmef.Set("alert.target(0).service.iana_protocol_number", 6)
        idmef.Set("alert.target(0).service.ip_version", 4)
        
        # Process
        idmef.Set("alert.source(0).process.name","honeytrap")
        
        # Assessment
        idmef.Set("alert.assessment.impact.severity", "info")
        
        idmef.Set("alert.assessment.impact.type", "other")
        idmef.Set("alert.assessment.impact.description", "Incoming connection to honeytrap TCP daemon")

        # Additional Data
        fieldsOffset = fieldsSet
        print "fieldsOffset = " + fieldsOffset.__str__()
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "p0f info")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", p0f)
                                        
        client.SendIDMEF(idmef)
        return
    
    except Exception,e:
        return
        
if __name__ == '__main__' :
    sendHoneytrapIDMEF("5.5.5.5","192.168.1.99","445","LNX","This is a test log entry")        
    
    