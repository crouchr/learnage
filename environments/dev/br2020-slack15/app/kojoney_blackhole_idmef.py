import time
import PreludeEasy
import kojoney_idmef_common

def sendBlackholeIDMEF(srcIP,text):
    try:
        attackerIP = srcIP
        logEntry   = "None"
        
        # Create a new Prelude client.
        client = PreludeEasy.ClientEasy("blackrain")
        client.Start()

        # Create the IDMEF message
        idmef = PreludeEasy.IDMEF()

        # Sensor                   
        fieldsSet = kojoney_idmef_common.setIDMEFcommon(idmef,"Honeypot","02DEBE56",srcIP,None,None,attackerIP,logEntry)
        
        # Classification
        idmef.Set( "alert.classification.text", text)

        # Source
        idmef.Set("alert.source(0).node.address(0).address", srcIP)
        
        # Location - this works ! 
        #idmef.Set("alert.source(0).node.location", "Hampshire")
        
        # Assessment
        idmef.Set("alert.assessment.impact.severity", "medium")
      
        idmef.Set("alert.assessment.impact.type", "recon")				# i.e. triggered by a port scan
        
        if "added" in text.lower() : 
            idmef.Set("alert.assessment.action(0).category" , "block-installed")	# Blackhole route added
        else:
            idmef.Set("alert.assessment.action(0).category" , "other")			# Block removed
          
        #idmef.Set("alert.assessment.action(1).category" , "notification-sent")		# Tweet generated
        
        client.SendIDMEF(idmef)
        return
    except Exception,e:
        print "exception : " + e.__str__()
        return
        
if __name__ == '__main__' :
    sendBlackholeIDMEF("15.5.5.105","Added blackhole")
    time.sleep(5)        
    sendBlackholeIDMEF("15.5.5.105","Removed blackhole")
    
    