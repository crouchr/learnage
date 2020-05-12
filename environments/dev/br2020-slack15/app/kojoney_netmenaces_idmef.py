import time
import PreludeEasy
import syslog
import ipintellib
import kojoney_idmef_common
import fileinput
import re
#import kojoney_cymru_hash

#ATTACKS = {'WebApp' : 'tcp,18080,192.168.1.62' , 'SSH' : 'tcp,2222,192.168.1.64' , 'SIP' : 'udp,5060,192.168.1.60' , 'Terminal Services server' : 'tcp,3389,192.168.1.60' , 'SQLSlammer' : 'udp,1433,192.168.1.60' , 'MSSQL' : 'tcp,1434,192.168.1.60'}
# Assign unique IP addresses against each Twitter Honeypot Feed from the 192.0.2.0/24 range
ATTACKS = {'WebApp' : 'tcp,18080,192.0.2.1,WebApp attack','SSH' : 'tcp,2222,192.0.2.1,SSH attack','SIP' : 'udp,5060,192.0.2.1,SIP attack','Terminal Services server' : 'tcp,3389,192.0.2.1,MS Terminal Services attack','SQLSlammer' : 'udp,1434,192.0.2.1,SQL Slammer attack','MSSQL' : 'tcp,1433,192.0.2.1,MS SQL attack'}

# @netmenaces honeypot
def sendNetmenacesIDMEF(line):
    try:
    
        global ATTACKS
        line = line.rstrip('\n')
        print line
        
        sock = 'NONE,0,0.0.0.0,NONE'		# N + zero
        for keyword in ATTACKS:
            if keyword in line :
                sock = ATTACKS[keyword]
                #print "socket attacked : " + sock.__str__()
        
        if sock == 'NONE,0,0.0.0.0,NONE':
            msg = "sendNetmenaces() : error : Unknown attack type in : " + line
            syslog.syslog(msg)
            return 
            
        ips = re.findall("\d+\.\d+\.\d+\.\d+",line)
        if len(ips) > 0 :
            srcIP      = ips[0]
            attackerIP = srcIP
            proto      = sock.split(',')[0]
            dstPort    = sock.split(',')[1]
            dstIP      = sock.split(',')[2]
            attackType = sock.split(',')[3]
            print "  ->  @netmenaces : attackType=" + attackType +  " attacker=" + srcIP + " dstIP=" + dstIP + " dstPort=" + dstPort + " proto=" + proto
        else:
            msg = "sendNetmenaces() : error : no IP address found in : " + line
            syslog.syslog(msg) 
            return 
                
        # Create a new Prelude client.
        client = PreludeEasy.ClientEasy("blackrain")
        client.Start()

        # Create the IDMEF message
        idmef = PreludeEasy.IDMEF()
                          
        # Sensor
        fieldsSet = kojoney_idmef_common.setIDMEFcommon(idmef,"Twitterverse","00000001",srcIP,dstIP,dstPort,attackerIP,line)
        
        # Classification
        #classification = attackType + " against #netmenaces Twitter Honeypot"
        #idmef.Set("alert.classification.text",classification)
    
        # Source
        idmef.Set("alert.source(0).node.address(0).address", srcIP)
        idmef.Set("alert.source(0).service.iana_protocol_name", proto)  
        idmef.Set("alert.source(0).service.ip_version", 4)
        
        # Target(s)
        idmef.Set("alert.target(0).node.address(0).address", dstIP)
        
        # Service
        idmef.Set("alert.target(0).service.iana_protocol_name", proto) 
        idmef.Set("alert.target(0).service.ip_version", 4)
        #idmef.Set("alert.target(0).service.name", service)
        idmef.Set("alert.target(0).service.port", dstPort)
        
        # Web Service specific details - override attackType
        if "GET" in line :
            idmef.Set("alert.target(0).service.web_service.http_method", "GET")
            attackType = "WebApp GET-based attack"
        elif "POST" in line :
            idmef.Set("alert.target(0).service.web_service.http_method", "POST")
            attackType = "WebApp POST-based attack"
        
        # Classification
        classification = attackType + " against @netmenaces Honeypot"
        idmef.Set("alert.classification.text",classification)
    
        # Assessment    
        idmef.Set("alert.assessment.impact.type", "other")
        #idmef.Set("alert.assessment.impact.completion", completion)
        #if completion == "succeeded" :
        #    idmef.Set("alert.assessment.impact.severity", "high")
        #else:
        idmef.Set("alert.assessment.impact.severity", "low")
        
        #idmef.Set("alert.assessment.impact.description", "Attempted Web Application Remote File Inclusion (RFI) attack")
        idmef.Set("alert.assessment.impact.description", "Honeypot event from @netmenaces Twitter-enabled Honeypot")
        
        # Additional Data
        #fieldsOffset = fieldsSet
        #print "fieldsOffset = " + fieldsOffset.__str__() 
        #idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        #idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "Apache CLF Record")
        #idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", apacheCLF)
        
        client.SendIDMEF(idmef)
        return

    except Exception,e:
        msg = "kojoney_netmences_idmef.py : sendNetmencesIDMEF() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return

# @evilafoot honeypot
EVILATTACKS = {'httpd' : 'tcp,18080,192.0.2.2,WebApp attack','epmapper' : 'tcp,135,192.0.2.2,MS EPMAPPER attack','SipSession' : 'udp,5060,192.0.2.2,SIP attack','mssqld' : 'tcp,1433,192.0.2.2,MS SQL attack','smbd' : 'tcp,445,192.0.2.2,MS SMBD attack'}

def sendEvilafootIDMEF(line):
    try:
    
        global EVILATTACKS
        line = line.rstrip('\n')
        
        line = line.replace(' )',')')		# annoying extra space in GeoIP info 
        #print line
        
        sock = 'NONE,0,0.0.0.0,NONE'		# N + zero
        for keyword in EVILATTACKS:
            tag = " used a " + keyword
            #print "sendEvilafoot() : tag=" + tag
            if tag in line :
                sock = EVILATTACKS[keyword]
                #print "socket attacked : " + sock.__str__()
        
        if sock == 'NONE,0,0.0.0.0,NONE':
            msg = "sendEvilafoot() : error : Unknown attack type in : " + line
            syslog.syslog(msg)
            return 
            
        ips = re.findall("\d+\.\d+\.\d+\.\d+",line)
        if len(ips) > 0 :
            srcIP      = ips[0]
            attackerIP = srcIP
            proto      = sock.split(',')[0]
            dstPort    = sock.split(',')[1]
            dstIP      = sock.split(',')[2]
            attackType = sock.split(',')[3]
            print "  ->  @evilafoot : attackType=" + attackType +  " attacker=" + srcIP + " dstIP=" + dstIP + " dstPort=" + dstPort + " proto=" + proto
        else:
            msg = "sendEvilafoot() : error : no IP address found in : " + line
            syslog.syslog(msg) 
            return 
                
        # Create a new Prelude client.
        client = PreludeEasy.ClientEasy("blackrain")
        client.Start()

        # Create the IDMEF message
        idmef = PreludeEasy.IDMEF()
                          
        # Sensor
        fieldsSet = kojoney_idmef_common.setIDMEFcommon(idmef,"Twitterverse","00000002",srcIP,dstIP,dstPort,attackerIP,line)
        
        # Source
        idmef.Set("alert.source(0).node.address(0).address", srcIP)
        idmef.Set("alert.source(0).service.iana_protocol_name", proto)  
        idmef.Set("alert.source(0).service.ip_version", 4)
        
        # Target(s)
        idmef.Set("alert.target(0).node.address(0).address", dstIP)
        
        # Service
        idmef.Set("alert.target(0).service.iana_protocol_name", proto) 
        idmef.Set("alert.target(0).service.ip_version", 4)
        #idmef.Set("alert.target(0).service.name", service)
        idmef.Set("alert.target(0).service.port", dstPort)
        
        # Classification
        classification = attackType + " against @evilafoot Honeypot"
        idmef.Set("alert.classification.text",classification)
    
        # Assessment    
        idmef.Set("alert.assessment.impact.type", "other")
        #idmef.Set("alert.assessment.impact.completion", completion)
        #if completion == "succeeded" :
        #    idmef.Set("alert.assessment.impact.severity", "high")
        #else:
        idmef.Set("alert.assessment.impact.severity", "low")
        
        #idmef.Set("alert.assessment.impact.description", "Attempted Web Application Remote File Inclusion (RFI) attack")
        idmef.Set("alert.assessment.impact.description", "Honeypot event from @evilafoot Twitter-enabled Honeypot")
        
        # Additional Data
        #fieldsOffset = fieldsSet
        #print "fieldsOffset = " + fieldsOffset.__str__() 
        #idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        #idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "Apache CLF Record")
        #idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", apacheCLF)
        
        client.SendIDMEF(idmef)
        return

    except Exception,e:
        msg = "kojoney_netmences_idmef.py : sendEvilafootIDMEF() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return

# @gjust SSHd honeypot
def sendGyustIDMEF(line):
    try:
    
        line = line.rstrip('\n')
        print line
        
        if "Royal Highness" not in line:
            return
                
        ips = re.findall("\d+\.\d+\.\d+\.\d+",line)
        if len(ips) > 0 :
            srcIP      = ips[0]
            attackerIP = srcIP
            proto      = "tcp"
            dstPort    = "2222"
            dstIP      = "192.0.2.3"
            attackType = "SSH attack"
            print "  ->  @gjust : attackType=" + attackType +  " attacker=" + srcIP + " dstIP=" + dstIP + " dstPort=" + dstPort + " proto=" + proto
        else:
            msg = "sendGyust() : error : no IP address found in : " + line
            syslog.syslog(msg) 
            return 
                
        # Create a new Prelude client.
        client = PreludeEasy.ClientEasy("blackrain")
        client.Start()

        # Create the IDMEF message
        idmef = PreludeEasy.IDMEF()
                          
        # Sensor
        fieldsSet = kojoney_idmef_common.setIDMEFcommon(idmef,"Twitterverse","00000003",srcIP,dstIP,dstPort,attackerIP,line)
        
        # Source
        idmef.Set("alert.source(0).node.address(0).address", srcIP)
        idmef.Set("alert.source(0).service.iana_protocol_name", proto)  
        idmef.Set("alert.source(0).service.ip_version", 4)
        
        # Target(s)
        idmef.Set("alert.target(0).node.address(0).address", dstIP)
        
        # Service
        idmef.Set("alert.target(0).service.iana_protocol_name", proto) 
        idmef.Set("alert.target(0).service.ip_version", 4)
        #idmef.Set("alert.target(0).service.name", service)
        idmef.Set("alert.target(0).service.port", dstPort)
        
        # Classification
        classification = attackType + " against @gjust Honeypot"
        idmef.Set("alert.classification.text",classification)
    
        # Assessment    
        idmef.Set("alert.assessment.impact.type", "other")
        #idmef.Set("alert.assessment.impact.completion", completion)
        #if completion == "succeeded" :
        #    idmef.Set("alert.assessment.impact.severity", "high")
        #else:
        idmef.Set("alert.assessment.impact.severity", "low")
        
        #idmef.Set("alert.assessment.impact.description", "Attempted Web Application Remote File Inclusion (RFI) attack")
        idmef.Set("alert.assessment.impact.description", "Honeypot event from @gjust Twitter-enabled Honeypot")
        
        # Additional Data
        #fieldsOffset = fieldsSet
        #print "fieldsOffset = " + fieldsOffset.__str__() 
        #idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        #idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "Apache CLF Record")
        #idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", apacheCLF)
        
        client.SendIDMEF(idmef)
        return

    except Exception,e:
        msg = "kojoney_netmences_idmef.py : sendGyustIDMEF() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return

        
if __name__ == '__main__' :
    
    # OPTION 1 
    # --------
    #for line in fileinput.input('/home/var/log/ext-hpot-netmenaces.log'):
    #    sendNetmenacesIDMEF(line)
    #    time.sleep(0.1)
    
    # OPTION 2 
    # --------
    #for line in fileinput.input('/home/var/log/ext-hpot-evilafoot.log'):
    #    sendEvilafootIDMEF(line)
    #    time.sleep(0.1)

    # OPTION 3 
    # --------
    for line in fileinput.input('/home/var/log/ext-hpot-gyust.log'):
        sendGyustIDMEF(line)
        time.sleep(0.1)

