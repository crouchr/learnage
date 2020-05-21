import PreludeEasy
import time
import kojoney_idmef_common

def sendSshIDMEF(srcIP,dstIP,dstPort,user,password,success,logEntry):
    try:
        #print "srcIP    : " + srcIP
        #print "dstIP    : " + dstIP
        #print "dtsPort  : " + dstPort
        #print "CC       : " + countryCode
        #print "username : " + user
        #print "password : " + password
        attackerIP = srcIP
        
        # Create a new Prelude client.
        client = PreludeEasy.ClientEasy("blackrain")
        client.Start()

        # Create the IDMEF message
        idmef = PreludeEasy.IDMEF()
        
        # Sensor                   
        fieldsSet = kojoney_idmef_common.setIDMEFcommon(idmef,"Honeypot","02DEBE56",srcIP,dstIP,dstPort,attackerIP,logEntry)
        
        # Classification
        idmef.Set( "alert.classification.text", "SSH honeypot login")

        # Source
        idmef.Set("alert.source(0).node.address(0).address", srcIP)
        #idmef.Set("alert.target(0).node.address(0).port", dstPort)

        # Target(s)
        idmef.Set("alert.target(0).node.address(0).address", dstIP)
        idmef.Set("alert.target(0).service.port", dstPort)
        
        idmef.Set("alert.target(0).service.iana_protocol_name", "tcp")
        idmef.Set("alert.target(0).service.iana_protocol_number", 6)
        idmef.Set("alert.target(0).service.ip_version", 4)
        
        idmef.Set("alert.target(0).user.category","application")
        idmef.Set("alert.target(0).user.user_id(0).type","target-user")
        idmef.Set("alert.target(0).user.user_id(0).name",user)
        
        idmef.Set("alert.source(0).process.name","kippo-sshd")
                    
        # Assessment
        if success == True:
            idmef.Set("alert.assessment.impact.severity", "high")
            idmef.Set("alert.assessment.impact.completion", "succeeded")
            idmef.Set("alert.assessment.impact.description", "Successful attempt to login to SSH Honeypot")
        else:
            idmef.Set("alert.assessment.impact.severity", "low")
            idmef.Set("alert.assessment.impact.completion", "failed")
            idmef.Set("alert.assessment.impact.description", "Failed attempt to login to SSH Honeypot")
        
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
        
        #idmef.Set("alert.additional_data(0).type", "string")
        #idmef.Set("alert.additional_data(0).meaning", "password")
        #idmef.Set("alert.additional_data(0).data", password)

        #idmef.Set("alert.additional_data(1).type", "string")
        #idmef.Set("alert.additional_data(1).meaning", "country")
        #idmef.Set("alert.additional_data(1).data", countryCode)

        result = client.SendIDMEF(idmef)
        #print result.__str__()
        return
    except Exception,e:
        print "Exception : " + e.__str__()
        return

def sendSshCmdIDMEF(srcIP,dstIP,dstPort,uid,cmd,logEntry):
    try:
        #print "srcIP    : " + srcIP
        #print "dstIP    : " + dstIP
        #print "dtsPort  : " + dstPort
        #print "CC       : " + countryCode
        #print "uid      : " + uid
        #print "command  : " + cmd
        attackerIP = srcIP
        
        # Create a new Prelude client.
        client = PreludeEasy.ClientEasy("blackrain")
        client.Start()

        # Create the IDMEF message
        idmef = PreludeEasy.IDMEF()
        
        # Sensor                   
        fieldsSet = kojoney_idmef_common.setIDMEFcommon(idmef,"Honeypot","02DEBE56",srcIP,dstIP,dstPort,attackerIP,logEntry)
                 
        # Classification
        idmef.Set( "alert.classification.text", "SSH command entered")

        # Source
        idmef.Set("alert.source(0).node.address(0).address", srcIP)
        #idmef.Set("alert.target(0).node.address(0).port", dstPort)

        # Target(s)
        idmef.Set("alert.target(0).node.address(0).address", dstIP)
        idmef.Set("alert.target(0).service.port", dstPort)
        
        # This works but not yet tied into Argus calling function
        idmef.Set("alert.target(0).service.iana_protocol_name", "tcp")
        idmef.Set("alert.target(0).service.iana_protocol_number", 6)
        idmef.Set("alert.target(0).service.ip_version", 4)

        #idmef.Set("alert.target(1).node.address(0).address", "10.0.0.3")
        
        #idmef.Set("alert.target(0).user.category","application")
        #idmef.Set("alert.target(0).user.user_id(0).type","target-user")
        #idmef.Set("alert.target(0).user.user_id(0).name",user)
        
        idmef.Set("alert.source(0).process.name","kippo-sshd")
                    
        # Assessment
        idmef.Set("alert.assessment.impact.severity", "high")
        idmef.Set("alert.assessment.impact.completion", "succeeded")
        idmef.Set("alert.assessment.impact.description", "User entered command in SSH Honeypot")
        
        if uid == "0" :
            idmef.Set("alert.assessment.impact.type", "admin")	
        else:
            idmef.Set("alert.assessment.impact.type", "user")	
            
        # Additional Data
        fieldsOffset = fieldsSet
        print "fieldsOffset = " + fieldsOffset.__str__()
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "command entered")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", cmd)
        fieldsOffset = fieldsOffset + 1
        
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "uid")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", uid.__str__())

        result = client.SendIDMEF(idmef)
        #print result.__str__()
        return
    except Exception,e:
        print "Exception : " + e.__str__()
        return


if __name__ == '__main__' :

    # Attacker entering commands
    # --------------------------
    sendSshCmdIDMEF("6.6.6.1","192.168.1.64","2222","0","# cd /home/haxx0r/leet_tools","This is a test log entry")
    time.sleep(0.2)
    #
    sendSshCmdIDMEF("6.6.6.2","192.168.1.64","2222","99","$ ls -laF","This is a test log entry")
    time.sleep(0.2)
    
    # Attacker Logging in
    # -------------------
    #sendSshIDMEF("6.6.6.6","192.168.1.64","2222","root","root123456",True,"This is a test log entry")
    #time.sleep(0.2)
    
    #sendSshIDMEF("8.6.6.6","192.168.1.64","2222","mysql","mysql123456",True,"This is a test log entry")
    #time.sleep(0.2)
    
    #sendSshIDMEF("9.6.6.6","192.168.1.64","2222","admin","admin123456",True,"This is a test log entry")
    #time.sleep(0.2)
    
    #sendSshIDMEF("11.6.6.6","192.168.1.64","2222","Admin","admin123456",True,"This is a test log entry")
    #time.sleep(0.2)
    
    # Failed
    #sendSshIDMEF("12.6.6.6","192.168.1.64","2222","root","tter123456",False,"This is a test log entry")
    #time.sleep(0.2)
    
    #sendSshIDMEF("13.6.6.6","192.168.1.64","2222","mysql","msd123456",False,"This is a test log entry")
    #time.sleep(0.2)
    
    #sendSshIDMEF("6.6.6.6","192.168.1.64","2222","Root","g44t123456",False,"This is a test log entry")
    #time.sleep(0.2)
    
