import time
import PreludeEasy
import syslog
import ipintellib
import kojoney_idmef_common
import kojoney_cymru_hash

# Clamd has located a virus in a network flow (via clsniffer)
def sendFlowClamdIDMEF(sensorId,srcIP,srcPort,dstIP,dstPort,clamavSig,line,tweet):
    try:
        
        # Create a new Prelude client.
        client = PreludeEasy.ClientEasy("blackrain")
        client.Start()

        # Create the IDMEF message
        idmef = PreludeEasy.IDMEF()

        # Sensor
        attackerIP = srcIP
        fieldsSet = kojoney_idmef_common.setIDMEFcommon(idmef,"Honeypot",sensorId,srcIP,dstIP,dstPort,attackerIP,line)
        
        # Classification
        idmef.Set("alert.classification.text","Malware detected in network flow")
    
        # Source
        idmef.Set("alert.source(0).node.address(0).address", srcIP)
        idmef.Set("alert.source(0).service.iana_protocol_name", "tcp")  
        idmef.Set("alert.source(0).service.ip_version", 4)
        idmef.Set("alert.source(0).service.port", srcPort)
        
        # Target(s)
        idmef.Set("alert.target(0).node.address(0).address", dstIP)
        idmef.Set("alert.target(0).service.iana_protocol_name", "tcp")  
        idmef.Set("alert.target(0).service.ip_version", 4)
        idmef.Set("alert.target(0).service.port", dstPort)
        
        # Service
        #idmef.Set("alert.target(0).service.iana_protocol_name", "tcp") 
        #idmef.Set("alert.target(0).service.ip_version", 4)
        #idmef.Set("alert.target(0).service.name", service)
        #idmef.Set("alert.target(0).service.port", dstPort)
        
        # Assessment    
        #idmef.Set("alert.assessment.impact.type", "other")
        idmef.Set("alert.assessment.impact.completion", "succeeded")
        idmef.Set("alert.assessment.impact.severity", "high")
        
        idmef.Set("alert.assessment.impact.description", "clsniffer detected malware in a netflow flow")
        
        # Additional Data
        fieldsOffset = fieldsSet
        print "fieldsOffset = " + fieldsOffset.__str__() 
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "ClamAV Signature")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", clamavSig)
        
        fieldsOffset = fieldsOffset + 1
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "Tweet")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", tweet.__str__())
        
        fieldsOffset = fieldsOffset + 1
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "sensorId")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", sensorId.__str__())
        
        client.SendIDMEF(idmef)
        return

    except Exception,e:
        msg = "kojoney_clamd_idmef.py : sendFlowClamdIDMEF : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return

        
if __name__ == '__main__' :
    tweet = "This is the test tweet"
    sendFlowClamdIDMEF("DEADBEEF","1.2.3.4","80","192.168.1.62","18080","TOTAL.DESTRUCTIOBOT-723","This is a log entry from the test harness, not a real event",tweet)
    
