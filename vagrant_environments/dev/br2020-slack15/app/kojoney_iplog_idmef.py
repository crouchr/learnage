import time
import PreludeEasy
import syslog

def portScanIDMEF(srcIP,scanType,dstPort,line):
#def sendWebAppIDMEF(attackType,url,service,dstPort,completion,srcIP,dstIP,geoIP):
    try:
        #username = username.rstrip()
        #password = password.rstrip()
        # bug - also truncate attacker entered fields to 64 characters
        
        # Create a new Prelude client.
        client = PreludeEasy.ClientEasy("blackrain")
        client.Start()

        # Create the IDMEF message
        idmef = PreludeEasy.IDMEF()

        # Sensor
        #idmef.Set("analyzer(-1).name", "honeytweeter")
        #idmef.Set("analyzer(-1).manufacturer", "Blackrain Technologies")
        #idmef.Set("analyzer(-1).class", "Honeypot")
        

        # Classification
        idmef.Set("alert.classification.text",scanType)

        #idmef.Set("alert.target(0).service.iana_protocol_name", "tcp")
        #idmef.Set("alert.target(0).service.iana_protocol_number", 6)  
        #idmef.Set("alert.target(0).service.ip_version", 4)
        #idmef.Set("alert.target(0).service.name", service)
        idmef.Set("alert.target(0).service.port", dstPort)
        #idmef.Set("alert.target(0).node.address(0).address", dstIP)
            
        # Source
        idmef.Set("alert.source(0).node.address(0).address", srcIP)
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
        idmef.Set("alert.assessment.impact.description", "Port scan detected against honeypot")
        
        #idmef.Set("alert.category" , "block-installed")


        # Additional Data
        idmef.Set("alert.additional_data(0).type", "string")
        idmef.Set("alert.additional_data(0).meaning", "Original log entry")
        idmef.Set("alert.additional_data(0).data", line.rstrip())
        
        client.SendIDMEF(idmef)
        return

    except Exception,e:
        msg = "kojoney_iplog_idmef.py : portScanIDMEF() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return
        
if __name__ == '__main__' :
    portScanIDMEF("7.7.7.7","TCP scan","22","Here is line from log")
    time.sleep(1)
    portScanIDMEF("7.7.7.7","UDP scan","53","Here is line from log")
    time.sleep(1)
    portScanIDMEF("7.7.7.7","SYN scan","25","Here is line from log")
    time.sleep(1)
    
    