# Test IDMEF client 
# this is not linked to any running code
import time
import PreludeEasy
import syslog
import kojoney_idmef_common

def sendIDMEF(sensorId,srcIP,dstIP,dstPort,attackerIP,logEntry):
    try:
        
        # Create a new Prelude client.
        #client = PreludeEasy.ClientEasy("honeytweeter")
        client = PreludeEasy.ClientEasy("blackrain")
        client.Start()

        # Create the IDMEF message
        idmef = PreludeEasy.IDMEF()

        # Sensor
        fieldsSet = kojoney_idmef_common.setIDMEFcommon(idmef,"test-honeypot",sensorId,srcIP,dstIP,dstPort,attackerIP,logEntry)
        
        # Classification
        idmef.Set("alert.classification.text","Test IDMEF message")

        idmef.Set("alert.target(0).service.iana_protocol_name", "tcp")
        idmef.Set("alert.target(0).service.iana_protocol_number", 6)  
        idmef.Set("alert.target(0).service.ip_version", 4)
        #idmef.Set("alert.target(0).service.name", service)
        #idmef.Set("alert.target(0).service.port", dstPort)
        idmef.Set("alert.target(0).node.address(0).address", "2.2.2.2")
            
        # Source
        idmef.Set("alert.source(0).node.address(0).address", srcIP)
        #idmef.Set("alert.source(0).user.user_id(0).name","target-user")
        
        #idmef.Set("alert.target(0).node.address(0).port", dstPort)

        # Target(s)
        #idmef.Set("alert.target(0).node.address(0).address", dstIP)
        #idmef.Set("alert.target(0).node.port", dstPort)

        #idmef.Set("alert.target(1).node.address(0).address", "10.0.0.3")

        #idmef.Set("alert.target(0).user.category","os-device")
        #idmef.Set("alert.target(0).user.user_id(0).type","target-user")
        #idmef.Set("alert.target(0).user.user_id(0).type","current-user")
        #idmef.Set("alert.target(0).user.user_id(0).name",username)
  
        
        # Assessment
        idmef.Set("alert.assessment.impact.severity", "info")
        #idmef.Set("alert.assessment.impact.completion", "succeeded")
        #idmef.Set("alert.assessment.impact.completion", completion)
        #idmef.Set("alert.assessment.impact.type", "user")
        #idmef.Set("alert.assessment.impact.type", "user")
        #idmef.Set("alert.assessment.impact.type", "other")
        idmef.Set("alert.assessment.impact.description", "This is a test message - ignore it")
        
        #idmef.Set("alert.category" , "block-installed")
        
        client.SendIDMEF(idmef)
        return fieldsSet

    except Exception,e:
        msg = "idmef_test.py : sendIDMEF() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return None
        
if __name__ == '__main__' :
    fieldsSet = sendIDMEF("dedbef","8.8.8.8","192.168.1.60","10023","8.8.8.8","This is the test log entry")
    print fieldsSet.__str__()
    