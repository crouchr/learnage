import PreludeEasy
import time
import kojoney_idmef_common

def sendTelnetIDMEF(srcIP,dstIP,dstPort,user,password,success,logEntry):
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
        idmef.Set("alert.classification.text", "Telnetd honeypot login")

        # Source
        idmef.Set("alert.source(0).node.address(0).address", srcIP)

        # Target(s)
        idmef.Set("alert.target(0).node.address(0).address", dstIP)
        idmef.Set("alert.target(0).service.port", dstPort)
        
        # This works but not yet tied into Argus calling function
        idmef.Set("alert.target(0).service.iana_protocol_name", "tcp")
        idmef.Set("alert.target(0).service.iana_protocol_number", 6)
        idmef.Set("alert.target(0).service.ip_version", 4)
        
        idmef.Set("alert.target(0).user.category","application")
        idmef.Set("alert.target(0).user.user_id(0).type","target-user")
        idmef.Set("alert.target(0).user.user_id(0).name",user)
        
        idmef.Set("alert.source(0).process.name","telnetd")
                    
        # Assessment
        if success == True:
            idmef.Set("alert.assessment.impact.severity", "high")
            idmef.Set("alert.assessment.impact.completion", "succeeded")
            idmef.Set("alert.assessment.impact.description", "Successful attempt to login to Telnet Honeypot")
        else:
            idmef.Set("alert.assessment.impact.severity", "low")
            idmef.Set("alert.assessment.impact.completion", "failed")
            idmef.Set("alert.assessment.impact.description", "Failed attempt to login to Telnet Honeypot")
        
        if user.lower() == "admin" or user.lower() == "root" :
            idmef.Set("alert.assessment.impact.type", "admin")	
        else:
            idmef.Set("alert.assessment.impact.type", "user")	
            
        # Additional Data
        fieldsOffset = fieldsSet
        print "fieldsOffset = " + fieldsOffset.__str__()
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "password")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", password)
        
        result = client.SendIDMEF(idmef)
        #print result.__str__()
        return
    except Exception,e:
        print "Exception : " + e.__str__()
        return
        
if __name__ == '__main__' :
    # Succeded
    sendTelnetIDMEF("6.6.6.6","192.168.1.69","10023","root","root123456",True,"This is a test log entry")
    time.sleep(0.2)
    
    sendTelnetIDMEF("6.6.6.6","192.168.1.69","10023","mysql","mysql123456",True,"This is a test log entry")
    time.sleep(0.2)
    
    sendTelnetIDMEF("6.6.6.6","192.168.1.69","10023","admin","admin123456",True,"This is a test log entry")
    time.sleep(0.2)
    
    sendTelnetIDMEF("6.6.6.6","192.168.1.69","10023","Admin","admin123456",True,"This is a test log entry")
    time.sleep(0.2)
    
    # Failed
    sendTelnetIDMEF("6.6.6.6","192.168.1.69","10023","root","tter123456",False,"This is a test log entry")
    time.sleep(0.2)
    
    sendTelnetIDMEF("6.6.6.6","192.168.1.69","10023","mysql","msd123456",False,"This is a test log entry")
    time.sleep(0.2)
    
    sendTelnetIDMEF("6.6.6.6","192.168.1.69","10023","Root","g44t123456",False,"This is a test log entry")
    time.sleep(0.2)
    
    