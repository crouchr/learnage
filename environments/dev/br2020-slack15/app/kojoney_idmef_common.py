import time , re
import PreludeEasy
import syslog
import ipintellib
import p0fcmd

# extract CGI and argument from URL
def extractCGI(url):
    try:
        if "?" in url:
            a = url.split("?")
            cgi = a[0]
            arg = a[1]
            print "URL:" + url + " -> cgi=" + cgi + " arg=" + arg
            return cgi,arg
        else:
            return None,None
                                                              
    except Exception,e:
        msg = "kojoney_idmef_common.py : extractCGI() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return
                                                                                                                                
# extract domain / IP from URL
def extractDomain(url):
    try:
        if '://' in url :
            a = url.split("://")  
            domain = a[1].split('/')[0]
            if ":" in domain :
                domain = domain.split(":")[0]
            print "url = " + url + " , domain = " + domain                                                                                                                                     
            #ips = re.findall("\d+\.\d+\.\d+\.\d+",domain)
            #if len(ips) > 0 :
            #    ip = ips[0]
            #else:
            #    ip = None    
            return domain
        else:
            return None
                                                                                                                                          
    except Exception,e:
        msg = "kojoney_idmef_common.py : extractDomain() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return None,None
                                                                                                                                                                                                                                                    
# Return the number of additional_data() rows filed this function
# srcIP,dstIP can be None
#
def setIDMEFcommon(idmef,analyserClass,sensorId,srcIP,dstIP,dstPort,attackerIP,logEntry) :
    try:
        print "kojoney_idmef_common.py : setIDMEFcommon() : srcIP      = " + srcIP.__str__()
        print "kojoney_idmef_common.py : setIDMEFcommon() : dstIP      = " + dstIP.__str__()
        #print "kojoney_idmef_common.py : setIDMEFcommon() : attackerIP = " + attackerIP.__str__()
        
        idmef.Set("alert.analyzer(0).model", "Blackrain")
        idmef.Set("alert.analyzer(0).name", "blackrain-" + sensorId.upper())
        idmef.Set("alert.analyzer(0).manufacturer", "Blackrain Technologies")
        idmef.Set("alert.analyzer(0).class", analyserClass)
        idmef.Set("alert.analyzer(0).version", "1.0rc1")
        idmef.Set("alert.analyzer(0).ostype", "Linux")
        idmef.Set("alert.analyzer(0).osversion", "2.6.21.5")
         
        if logEntry != None:
            logEntry = logEntry.rstrip()
        else:
            logEntry = "None"    
        idmef.Set("alert.additional_data(0).type", "string")
        idmef.Set("alert.additional_data(0).meaning", "Original log entry")
        idmef.Set("alert.additional_data(0).data", logEntry)
        print "kojoney_idmef_common.py : setIDMEFcommon() : logEntry   = " + logEntry.__str__()
         
        fieldsSet = 1
        
        if attackerIP != None:
            # GeoIP enhancement
            geoIP = ipintellib.geo_ip(attackerIP)
            #print geoIP.__str__()
            countryCode = geoIP['countryCode'].__str__()
            city        = geoIP['city'].__str__()
            
            # Prewikka has a "spare" pie-chart used for source users - so abuse it for Country Code pie-chart
            idmef.Set("alert.source(0).user.user_id(0).name","haxx0r-" + countryCode)
            idmef.Set("alert.source(0).user.user_id(0).tty","UserId Name is faked")
             
            if attackerIP == srcIP :
                idmef.Set("alert.source(0).node.location", countryCode)
                addInfoLabel = "Source(0) "
            elif attackerIP == dstIP:
                idmef.Set("alert.target(0).node.location", countryCode)
                addInfoLabel = "Target(0) "
            
            latitude  = "%.2f" % geoIP['latitude'] + " N" 
            longitude = "%.2f" % geoIP['longitude'] + " E"

            # AS enhancement
            asInfo = ipintellib.ip2asn(attackerIP)                                                      
            #print asInfo.__str__()
            asNum = asInfo['as'].__str__()                                                 
            asRegisteredCode = asInfo['registeredCode'].__str__()   
            asRegisteredName = asInfo['registeredName'].__str__()   
            asNetblock  = asInfo['netblock'].__str__()   
            asRegistry  = asInfo['registry'].__str__()   
        
            idmef.Set("alert.additional_data(1).type", "string")
            idmef.Set("alert.additional_data(1).meaning", addInfoLabel + "MaxMind GeoIP City")
            idmef.Set("alert.additional_data(1).data", city)
        
            idmef.Set("alert.additional_data(2).type", "string")
            idmef.Set("alert.additional_data(2).meaning", addInfoLabel + "MaxMind GeoIP Latitude")
            idmef.Set("alert.additional_data(2).data", latitude)
        
            idmef.Set("alert.additional_data(3).type", "string")
            idmef.Set("alert.additional_data(3).meaning", addInfoLabel + "MaxMind GeoIP Longitude")
            idmef.Set("alert.additional_data(3).data", longitude)
        
            idmef.Set("alert.additional_data(4).type", "string")
            idmef.Set("alert.additional_data(4).meaning", addInfoLabel + "BGP ASN")
            idmef.Set("alert.additional_data(4).data", "AS" + asNum)
        
            idmef.Set("alert.additional_data(5).type", "string")
            idmef.Set("alert.additional_data(5).meaning", addInfoLabel + "ISP Code")
            idmef.Set("alert.additional_data(5).data", asRegisteredCode)
        
            idmef.Set("alert.additional_data(6).type", "string")
            idmef.Set("alert.additional_data(6).meaning", addInfoLabel + "ISP Name")
            idmef.Set("alert.additional_data(6).data", asRegisteredName)
        
            idmef.Set("alert.additional_data(7).type", "string")
            idmef.Set("alert.additional_data(7).meaning", addInfoLabel + "Internet prefix/route")
            idmef.Set("alert.additional_data(7).data", asNetblock)
        
            idmef.Set("alert.additional_data(8).type", "string")
            idmef.Set("alert.additional_data(8).meaning", addInfoLabel + "Internet Registry")
            idmef.Set("alert.additional_data(8).data", asRegistry)
        
            fieldsSet = fieldsSet + 8
        
        # p0f enhancement - optional
        if srcIP != None and dstIP != None and dstPort != None:
            p0fInfo = p0fcmd.getP0fInfo(srcIP,"0",dstIP,dstPort);           # 0 = wildcard the srcPort
            if p0fInfo['result'] == True :                                  # p0f data is available   
                os   = p0fInfo['genre']
                nat  = p0fInfo['nat'][0]
                hops = p0fInfo['hops']
                idmef.Set("alert.additional_data(9).type", "string")
                idmef.Set("alert.additional_data(9).meaning", "p0f : OS")
                idmef.Set("alert.additional_data(9).data", os.__str__())
            
                idmef.Set("alert.additional_data(10).type", "string")
                idmef.Set("alert.additional_data(10).meaning", "p0f : NAT detected")
                idmef.Set("alert.additional_data(10).data", nat.__str__())
            
                idmef.Set("alert.additional_data(11).type", "string")
                idmef.Set("alert.additional_data(11).meaning", "p0f : IP hops")
                idmef.Set("alert.additional_data(11).data", hops.__str__())
                fieldsSet = fieldsSet + 3
        
        #print "fieldsSet = " + fieldsSet.__str__()    
        return fieldsSet
                                                            
    except Exception,e:
        msg = "kojoney_idmef_common.py : setIDMEFcommon() : exception : " + e.__str__()
        print msg
        syslog.syslog(msg)
        return None


# test using idmef_test.py
    