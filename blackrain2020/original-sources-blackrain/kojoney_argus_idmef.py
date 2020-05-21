import PreludeEasy
import kojoney_idmef_common

# need port numbers for both incoming and outgoing - remember PAT on inbound 18080 etc
ARGUS_PORTLIST = {
      '80':'HTTP',
     '443':'HTTPS',
     '110':'POP3',
    '5900':'VNC',
    '1080':'SOCKS',
    '4899':'RADMIN',
   '18080':'HTTP',
    '2222':'SSH',
   '10023':'TELNET',
   '10025':'SMTP',
    '3389':'RDP',
    '3306':'MYSQL',
     '445':'CIFS',
      '53':'DNS',
     '161':'SNMP',
    '5060':'SIP',
    '1433':'MSSQL',
    '1434':'MSSQL',
     '135':'MSRPC',
     '137':'MS_NBNAME',
     '138':'MS_NBDGRAM',
     '139':'MS_NBSESSION',
      '69':'TFTP',
      '20':'FTP20',
      '21':'FTP21'
   }
   
   
def mapPortNumber(port):   
    try:
       #print "port = " + port
       for i in ARGUS_PORTLIST:
           #print "i = " + i
           if port == i :
               return ARGUS_PORTLIST[i]
       else:
           #print "Could not locate port : " + port
           return ""
    except Exception,e:
        print "mapPortNumber() : exception : " + e.__str__()
        return
    
def sendArgusIDMEF(srcIP,dstIP,dstPort,protocol,dir,flags,pkts,bytes,p0f,hops,FLOW_TYPE):
    try:
        
        if FLOW_TYPE == "AFLOW_IN" :
            direction = "Inbound "
        elif FLOW_TYPE == "AFLOW_OUT" :
            direction = "Outbound "
        else:
            direction = ""            
            return None	# radical - why are there flows that are not In or Out ?
            
        portName = mapPortNumber(dstPort)
        
        if int(bytes) >= 1024 or int(pkts) >= 32 :
            size = "Long "
            direction = direction.lower()
        else :
            size = ""
        
        # Create a new Prelude client.
        client = PreludeEasy.ClientEasy("blackrain")	# blackrain = Profile
        client.Start()
                                
        # Create the IDMEF message
        idmef = PreludeEasy.IDMEF()

        # Sensor
        if "nbound" in direction :	# attackerIP = srcIP
            fieldsSet = kojoney_idmef_common.setIDMEFcommon(idmef,"Honeypot","02DEBE56",srcIP,dstIP,dstPort,srcIP,"None")
            idmef.Set("alert.assessment.impact.severity", "info")	# normal inbound flows
        
        elif "utbound" in direction :	# attackerIP = dstIP
            fieldsSet = kojoney_idmef_common.setIDMEFcommon(idmef,"Honeypot","02DEBE56",srcIP,dstIP,dstPort,dstIP,"None")
            idmef.Set("alert.assessment.impact.severity", "high")	# outgoing session !
        else:
            return None		# code should never get here
        
        #if protocol == "OTHER" :
        #    protocol = ""
                
        classification = size + direction + protocol + " ArgusFlow " + portName
        classification = classification.rstrip(" ")
        #print "argus IDMEF classification = [" + classification + "]"
            
        # Classification
        #idmef.Set("alert.classification.text", "ARGUS flow")
        idmef.Set("alert.classification.text", classification)

        # Source
        idmef.Set("alert.source(0).node.address(0).address", srcIP)
        #idmef.Set("alert.target(0).node.address(0).port", dstPort)

        # Target(s)
        idmef.Set("alert.target(0).node.address(0).address", dstIP)
        idmef.Set("alert.target(0).service.port", dstPort)
        
        # Set protcol if one of the well known ones
        if protocol == "TCP" :
            idmef.Set("alert.target(0).service.iana_protocol_name", "tcp")
            idmef.Set("alert.target(0).service.iana_protocol_number", 6)
        elif protocol == "UDP" : 
            idmef.Set("alert.target(0).service.iana_protocol_name", "udp")
            idmef.Set("alert.target(0).service.iana_protocol_number", 17)
        elif protocol == "ICMP" : 
            idmef.Set("alert.target(0).service.iana_protocol_name", "icmp")
            idmef.Set("alert.target(0).service.iana_protocol_number", 1)
            
        idmef.Set("alert.target(0).service.ip_version", 4)

        # Assessment
        idmef.Set("alert.assessment.impact.type", "other")
        idmef.Set("alert.assessment.impact.description", "flow")

        # Additional Data
        #idmef.Set("alert.additional_data(0).type", 	"string"	)
        #idmef.Set("alert.additional_data(0).meaning", 	"flags"		)
        #idmef.Set("alert.additional_data(0).data", 	flags.__str__() )
        
        #idmef.Set("alert.additional_data(1).type", 	"string"	)
        #idmef.Set("alert.additional_data(1).meaning", 	"pkts"		)
        #idmef.Set("alert.additional_data(1).data", 	pkts.__str__())
        
        #idmef.Set("alert.additional_data(2).type", 	"string"	)
        #idmef.Set("alert.additional_data(2).meaning", 	"bytes"		)
        #idmef.Set("alert.additional_data(2).data", bytes.__str__())
        
        #idmef.Set("alert.additional_data(3).type", 	"string"	)
        #idmef.Set("alert.additional_data(3).meaning", 	"clientOS"		)
        #idmef.Set("alert.additional_data(3).data", p0f.__str__())
        
        #idmef.Set("alert.additional_data(4).type", 	"string"	)
        #idmef.Set("alert.additional_data(4).meaning", 	"direction"		)
        #idmef.Set("alert.additional_data(4).data", dir.__str__())
        
        #idmef.Set("alert.additional_data(5).type", 	"string"	)
        #idmef.Set("alert.additional_data(5).meaning", 	"IP hops"		)
        #idmef.Set("alert.additional_data(5).data",  hops.__str__())

        client.SendIDMEF(idmef)
        return
    except Exception,e:
        print "sendArgusIDMEF() : exception : " + e.__str__()
        return
        
if __name__ == '__main__' :
    pass
    sendArgusIDMEF("5.5.5.5","192.168.1.99","445","sSE")        
    
