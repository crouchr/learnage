#!/usr/bin/python
# /usr/local/bin/python


import re , sys
import syslog
import blackrain_ipintellib
import kojoney_p0f_lib

# Convert decimal logical OR of TCP flags to their flag names
def netflowFlags(flagsString):
    
    flags = int(flagsString)
    
    if flags == 0 :
        return "X"
            
    flagsStr = ""
    if flags & 32 != 0 :
        flagsStr = flagsStr + "U"
    if flags & 16 != 0 :
        flagsStr = flagsStr + "A"
    if flags & 8 != 0 :
        flagsStr = flagsStr + "P"
    if flags & 4 != 0 :
        flagsStr = flagsStr + "R"
    if flags & 2 != 0 :
        flagsStr = flagsStr + "S"
    if flags & 1 != 0 :
        flagsStr = flagsStr + "F"
                                                                                      
    #print "netflowFlags() result is " + flagsStr
    return flagsStr
                                                                                              
# x is an integer
#def icmpDecode(x):
#    type = int(x/256)
#    code = x % 256
#    icmpStr = "T=" + `type` + ":C=" + `code`
#                                                                                                          
#    #print "icmpDecode() : result is " + icmpStr                
#    return icmpStr
                                                                                                                  
def processNetflow(line):
    flowEvent = {}
    
    try : 
        #print "-> Entered blackrain_netflow.processNetflow()"
        #print line
        #print hpotIP
        
        flowEvent['flowType']       = "FLOW_NETFLOW_V5"
        
        sIP = re.findall("sIP=(\d+.\d+.\d+.\d+)",line)[0] 
        sP  = re.findall("sP=(\d+)",line)[0] 
        dIP = re.findall("dIP=(\d+.\d+.\d+.\d+)",line)[0] 
        dP  = re.findall("dP=(\d+)",line)[0] 
        
        if line.find("dir=in") != -1 :
            flowEvent['flowDirection'] = "in"
        else:    
            #print "** OUTBOUND **"
            flowEvent['flowDirection'] = "out"
        
        if flowEvent['flowDirection'] == "out" :
            flowEvent['flowRemoteIP']   = dIP 
            flowEvent['flowHpotIP']     = sIP 
            flowEvent['flowRemotePort'] = dP 
            flowEvent['flowHpotPort']   = sP 
        else :
            flowEvent['flowRemoteIP']   = sIP 
            flowEvent['flowHpotIP']     = dIP 
            flowEvent['flowRemotePort'] = sP 
            flowEvent['flowHpotPort']   = dP

        proto = re.findall("pr=(\d+)",line)[0] 
        if proto == "1" :
            flowEvent['flowProto'] = "I" 
        elif proto == "6" :
            flowEvent['flowProto'] = "T" 
        elif proto == "17" :
            flowEvent['flowProto'] = "U" 
        else : 
            flowEvent['flowProto'] = proto	# just the protocol number 

        # OS
        p0fDict = kojoney_p0f_lib.getp0f(sIP,dIP,dP)
        if p0fDict != None:
            flowEvent['flowOS']    = p0fDict['genre']
        else:
            flowEvent['flowOS']    = "-"
            #flowEvent['flowOS']    = "next release !"
        
        # Optional parameters    
        flowEvent['flowDuration'] = re.findall("t=(\d+)" ,line)[0] 
        flowEvent['flowPkts']     = re.findall("p=(\d+)" ,line)[0] 
        flowEvent['flowBytes']    = re.findall("B=(\d+)" ,line)[0] 
        flowEvent['flowTflags']   = netflowFlags(re.findall("fl=(\d+)",line)[0]) 
        
        # Data enrichment
        if flowEvent['flowDirection'] == "in" :
            # DNS info
            dnsInfo = blackrain_ipintellib.ip2name(flowEvent['flowRemoteIP'])
            flowEvent['flowDNS'] = dnsInfo['name'].rstrip('.')   

            # GeoIP info
            geoIP = blackrain_ipintellib.geo_ip(flowEvent['flowRemoteIP'])
            flowEvent['flowCC']      = geoIP['countryCode']      
            flowEvent['flowCountry'] = geoIP['countryName']     
            flowEvent['flowCity']    = geoIP['city']
            flowEvent['flowLat' ]    = "%.3f" % float(geoIP['latitude'])                          
            flowEvent['flowLong' ]   = "%.3f" % float(geoIP['longitude'])                         
        
            # WHOIS info        
            asInfo = blackrain_ipintellib.ip2asn(flowEvent['flowRemoteIP'])
            if asInfo['as'] == "AS-none":
                msg = "blackrain_netflow.py : ip2asn() failed for ip=" + flowEvent['flowRemoteIP'].__str__() + " line=" + line
                syslog.syslog(msg)
            flowEvent['flowASN']    = asInfo['as']   		       		# AS123   
            flowEvent['flowISP']    = asInfo['registeredCode']		     	# Short-form e.g. LEVEL3
            flowEvent['flowRoute']  = asInfo['netblock']	
            flowEvent['flowRIR']    = asInfo['registry']	
        else :		# Flow originates from honeypot so add in fake info
            # DNS info
            flowEvent['flowDNS'] = "-"   

            # GeoIP info
            #geoIP = blackrain_ipintellib.geo_ip(flowEvent['flowRemoteIP'])
            flowEvent['flowCC']      = "-"      
            flowEvent['flowCountry'] = "-"     
            flowEvent['flowCity']    = "-"
            flowEvent['flowLat' ]    = "999.000"                          
            flowEvent['flowLong' ]   = "999.000"                         
        
            # WHOIS info        
            #asInfo = blackrain_ipintellib.ip2asn(flowEvent['flowRemoteIP'])
            flowEvent['flowASN']    = "-"   		   
            flowEvent['flowISP']    = "-"		
            flowEvent['flowRoute']  = "-"	
            flowEvent['flowRIR']    = "-"
        
        #print flowEvent.__str__()                                       
        return flowEvent
            
    except Exception,e :
        msg = "blackrain_netflow.py : exception " + e.__str__() + " in line=" + line
        print msg
        syslog.syslog(msg)
    

#Feb 22 09:00:15 mars blackrain_netflow: dir=out sIP=192.168.1.60 sP=43576 dIP=216.137.45.1 dP=80 pr=6 B=40 p=1 fl=4 t=0
#Feb 22 09:00:15 mars blackrain_netflow: dir=in sIP=216.137.45.1 sP=80 dIP=192.168.1.60 dP=43576 pr=6 B=44 p=1 fl=18 t=0
#Feb 22 09:01:10 mars blackrain_netflow: dir=in sIP=81.88.221.207 sP=1114 dIP=192.168.1.69 dP=10023 pr=6 B=296 p=6 fl=215 t=944
#Feb 22 09:01:10 mars blackrain_netflow: dir=out sIP=192.168.1.69 sP=10023 dIP=81.88.221.207 dP=1114 pr=6 B=404 p=4 fl=27 t=656
#Feb 22 09:58:07 mars blackrain_netflow: netflow_record dir=out sIP=192.168.1.69 sP=10023 dIP=81.170.242.41 dP=4532 pr=6 B=456 p=5 fl=27 t=908
#Feb 22 09:58:07 mars blackrain_netflow: netflow_record dir=in sIP=81.170.242.41 sP=4532 dIP=192.168.1.69 dP=10023 pr=6 B=336 p=7 fl=23 t=1288
#Feb 22 09:58:27 mars blackrain_netflow: netflow_record dir=in sIP=79.20.111.42 sP=40978 dIP=192.168.1.60 dP=25429 pr=17 B=95 p=1 fl=0 t=0
#Feb 22 09:58:27 mars blackrain_netflow: netflow_record dir=out sIP=192.168.1.60 sP=3 dIP=79.20.111.42 dP=3 pr=1 B=123 p=1 fl=0 t=0
#Feb 22 10:00:52 mars blackrain_netflow: netflow_record dir=out sIP=192.168.1.62 sP=18080 dIP=220.168.128.90 dP=58205 pr=6 B=492 p=6 fl=27 t=1228
#Feb 22 10:00:52 mars blackrain_netflow: netflow_record dir=in sIP=220.168.128.90 sP=58205 dIP=192.168.1.62 dP=18080 pr=6 B=367 p=7 fl=31 t=1752


# test harness

if __name__ == '__main__' :
    fp = open('/home/var/log/netflow.syslog','r')
    
    while True:
        
        line = fp.readline()
        
        if not line :
            sys.exit()
        
        print "------------"    
        print processNetflow(line)
