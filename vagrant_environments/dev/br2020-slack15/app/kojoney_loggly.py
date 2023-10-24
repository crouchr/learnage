#!/usr/bin/python

import time, os , syslog , re 
import httplib2
import ipintellib
import simplejson as json
import crudeTld			# rch : fixme - not a complete solution but good enough on Python 2.6
from pprint import pprint

# User account = honeypotr , pass = fuckloggly99 / email = uber.koob@gmail.com
# my login domain is honeytweeter.loggly.com
txnId  = 0
txnId2 = 0

# A test function - move into a library : fixme
def writeToSyslogFake(msg):
    syslogFmt = time.ctime() + "mars kojoney_logglyd[666]: " + '"' + msg + '"'
    fpOut = open("/home/var/log/blackrain-json.log","a")
    print >> fpOut,syslogFmt
    fpOut.close()
    

# process a honeypot host system /var/log/message and send to SplunkCloud LaaS
def sendToSplunkPlatform(sensorId,line,log):
    
    try :
        global txnId2                    
        sdata = {}
        
        # Txnid2 - increment this last, just before submission to Loggly
        txnId2 = txnId2 + 1
        sdata['txnId'] = txnId2

        # Sensor Name
        sdata['sensorId'] = sensorId

        # Syslog message
        sdata['msg'] = line
        
        # IP address
        ips = re.findall("\d+\.\d+\.\d+\.\d+",line)
        if len(ips) > 0 :
            sdata['ip'] = ips[0]
            
        # Track exceptions from Twitter API
        if "TweepError" in line :
            sdata['subsystem'] = "Twitter"

        # Splunk
        print "\nkey-value pairs for Splunk Platform Project :-"
        splunkMsg = "'" + time.ctime() + ' ' + sensorId 
        for i in sdata:
            splunkMsg = splunkMsg + ' ' + i.__str__() + '=' + '"' + sdata[i].__str__() + '"'
            #print i,sdata[i]
        
        #splunkMsg = splunkMsg + "'"
        #print "SplunkCloud msg=" + splunkMsg
        #log.send(splunkMsg , sourcetype='syslog',host=sensorId)

        # crude form of rate-limiter
        time.sleep(0.5)
                                 
    except Exception,e:
        msg = "kojoney_loggly.py : sendToSplunkPlatform() : exception : " + e.__str__() + " line=" + line
        print msg
        
# process a Tweet Queue message and submit to ELK
def sendToLoggly(sensorId,line):
    
    try :
        global txnId                    
        
        print "sendToLoggly() : line=" + line

        # honeytweeter
        #shakey = "e25e6042-e490-4910-a246-94cefbdd11b9"               
        
        # honeytweeter-json
        shakey = "fe39eb54-7c8f-417c-afc8-5b8db98961d3"               

        sdata = {}
        cifdata = {}

        # Event Type
        fields = line.split(",")
        eventType = fields[0]
        sdata['eventType'] = fields[0]
        
        # Do not process obsolete eventTypes
        if sdata['eventType'] == 'FW_SNORT' or sdata['eventType'] == 'NIDS_SH' : 
            return None

        if sdata['eventType'] == "ANALYST" and  "TRACEROUTE" in line : 	# ANALYST traceroutes don't visualise well
            return None
        
        if sdata['eventType'] == "ANALYST" and  "NMAP" in line : 	# ANALYST nmaps don't visualise well
            return None
            
        #print sdata['eventType']
                
        # Sensor Name
        sdata['sensorId'] = sensorId
        
        # IP address
        ips = re.findall("\d+\.\d+\.\d+\.\d+",line)
        if len(ips) > 0 :
            sdata['ip'] = ips[0]
            
            # GeoIP
            geoIP = ipintellib.geo_ip(sdata['ip'])   
            cc = geoIP['countryCode']
            if cc != "?" :
                sdata['cc'] = cc.__str__()         
                sdata['ipcc'] = sdata['ip'].__str__() + " - " + sdata['cc'].__str__()
                
            # Reverse DNS : fixme Extract the TLD and create a sdata field for it
            dnsInfo = ipintellib.ip2name(sdata['ip'])
            dnsName = dnsInfo['name']
            if dnsName != "NoDNS":
                sdata['rdns'] = dnsName.rstrip('.').lower()            
                sdata['tld']  = crudeTld.getTLD(sdata['rdns'])
                if "baiduspider" in sdata['rdns'] :
                    return None # this is not an interesting event
                if sdata['rdns'] == "pointer" :
                    return None
                    
            # ASN info
            asInfo = ipintellib.ip2asn(sdata['ip']) 
            asNum = asInfo['as']                                                # AS123
            if asNum == "AS-none" :
                asNum = "NO_INFO"
            else :
                asNum = "AS" + asNum       
            asRegisteredCode = asInfo['registeredCode'].upper()                 # e.g. GOOGLE
            sdata['asn'] = asNum
            sdata['isp'] = asRegisteredCode                           

        # Snort SID
        if sdata['eventType'] == "SNORT_NIDS" or sdata['eventType'] == "NIDS_SH" :
            sids = re.findall("SID=(\d+)",line)
            if len(sids) > 0:
                sdata['sid'] = sids[0]
            a = re.findall("P(\d+) SID",line)
            if len(a) > 0 :
                sdata['priority'] = a[0]
                # removed the P from the priority - due to ELK issues - fixme : make a Blackrain-wide PRIORITY ? for all events ? 
        
        # Clamd malware name - e.g. Exploit.Shellcode.X86-Gen-1
        # Jun 27 04:47:39 mars kojoney_tweet_engine[3173]: SENDTWEET = <0>CLAMD,Malware Exploit.Shellcode.X86-Gen-1 in flow from 79.5.203.86 ports={s=4592 d=135}
        if sdata['eventType'] == "CLAMD" :
            a = line.split(",Malware ")[1]
            a = a.split(" ")[0]
            sdata['malware'] = a
            sdata['avendor'] = "ClamAV"
            
        # Threat Report
        # submitted=Wed Jun 26 02:54:18 2013 cmd=GEO_IP tweet=REPORT,Threat Level for 203.250.135.20 is 41.1, flags={PR SC PS BH AT GA}
        if "flags={" in line and sdata['eventType'] == "REPORT" :
            a = line.split("flags=")[1]
            #a = a.rstrip("}")
            sdata['flags'] = a
        
        # VirusTotal    
        # submitted=Fri May 17 07:48:03 2013 cmd=BASIC tweet=ANALYST,AV eb7656dd256eb414abe092eb0f41ea1f.php => Norman=PhpShell.BL 17/46 VT=http://bit.ly/14vyont
        # line=ANALYST,AV 06a940dd7824d6a3a6d5b484bb7ef9d5.php => Unseen by VirusTotal
        if sdata['eventType'] == "ANALYST" and "AV" in line and "Unseen by" not in line :
            a = line.split(" => ")[1]
            b = a.split(" ")[0]		# Symantec=Trojan.Usuge!gen3
            sdata['avendor'] = b.split("=")[0]    
            sdata['malware'] = b.split("=")[1]             
            
            b = a.split("VT=")[1]
            sdata['virustotal'] = b
            
            # filename = MD5 name + extension (optional)
            c = line.split("AV ")[1]
            c = c.split(" ")[0]
            #print c
            if "." in c:
                c = c.split(".")[0]	# lose filename extension 
            sdata['md5'] = c.lower()
            
        # Destination port - make this a string so it is not displayed with commas in Kibana    
        # ----------------------------------------------------------------------------------
        # Snort messages
        flow = re.findall("\w+\:(\d+) ",line)    
        if len(flow) > 0 :
            sdata['port'] = str(flow[0])    
        
        # IPLOG - make a string so it is displayed with commas in Kibana
        # --------------------------------------------------------------    
        if sdata['eventType'] == "IPLOG" :
           ports = re.findall("port (\d+)",line)    
           if len(ports) > 0 :
               sdata['port'] = str(ports[0])

        # CLAMD - clsniffer    
        if sdata['eventType'] == "CLAMD" :
           ports = re.findall("d=(\d+)",line)    
           if len(ports) > 0 :
               sdata['port'] = str(ports[0])
        
        # KIPPO
        if sdata['eventType'] == "KIPPO" :
            #sdata['port'] = 2222
            sdata['port'] = "22"
            sdata['protocol'] = "tcp"
        
        ############
        # Glastopf #       
        ############
        if "WEB_" in sdata['eventType'] :
            #sdata['port'] = 18080    
            sdata['port'] = "80"    
            sdata['protocol'] = "tcp"       
            line = line.replace('|','/') 	# pipe character is used in Tweets to avoid Twitter generating shortened URLs 
            url = line.split('req=')[1]
            sdata['url'] = url.lower()
            #if sdata['url'] == '/' or sdata['url'] == '//' :
            #    return None 


        # Botjuicer cracked scripts
        if sdata['eventType'] == "ANALYST" and "BOTJUICER" in line :
            #if "UNDETERMINED" in line.upper():
            #    return None
            #print "BOTJUICER log found : " + line
            a = re.findall("p=(\d+)",line)
            if len(a) > 0 : 
                sdata['port'] = str(a[0])
            a = re.findall("ch=(#\w+)",line)
            if len(a) > 0 : 
                sdata['irc'] = a[0]
                      
        # Protocol - generic    
        if "TCP" in line.upper():
            sdata['protocol'] = "tcp"
        if "UDP" in line.upper():
            sdata['protocol'] = "udp"
        if "ICMP" in line.upper():
            sdata['protocol'] = "icmp"
              
        # Timestamp
        sdata['datetime'] = time.ctime()
        
        # Message
        sdata['msg'] = line.split(",")[1:][0]
                
        # Txnid - increment this last, just before submission to Loggly
        txnId = txnId + 1
        sdata['txnId'] = txnId

        # Splunk
        #print "\nkey-value pairs for Splunk :-"
        #splunkMsg = "'" + time.ctime() + ' ' + sensorId + ' '
        #for i in sdata:
        #    if i == 'datetime' : # ignore
        #        continue 
        #    if i == 'msg' and "SNORT" in eventType:
        #        print "Snort event found"
        #    #    sdata[i] = '"' + sdata[i] + '"'
        #    #    sdata[i] = sdata[i].replace('"','')
        #    splunkMsg = splunkMsg + ' ' + i.__str__() + '=' + '"' + sdata[i].__str__() + '"'
        #    #print i,sdata[i]
        #splunkMsg = splunkMsg + "'"
        
        # Abandoned - has my API key run out ?
        #print "Send to SplunkStorm Cloud SIEM => " + splunkMsg
        #log.send(splunkMsg , sourcetype='syslog',host=sensorId)
                
        # Loggly - abandoned in favour of splunk         
        #body = json.dumps(sdata)        
        
        #print "\nsendToLoggly() : JSON body = " + body
                         
        # Send to Loggly
                         
        #insert_url = "http://logs.loggly.com/inputs/" + shakey
        #insert_http = httplib2.Http(timeout=10)
        ##body = line
        #resp, content = insert_http.request(insert_url, "POST", body=body, headers={'content-type':'text/plain'})
        ##print "Loggly : resp : " + resp.__str__()
        ##print "Loggly : content : " + content.__str__()             
        
        ##{'status': '200', 'content-length': '18', 'vary': 'Accept-Encoding', 'server': 'TwistedWeb/12.0.0', 'date': 'Tue, 25 Jun 2013 05:55:58 GMT', 'content-type': 'text/html'}
        ##{"response": "ok"}
        
        #if "ok" in content.__str__() :		# bug -> why can't I look at the "response" field in a structured way
        #    msg = "Sent to Loggly OK : " + body.__str__()
        #    print msg
        #else:
        #    msg = "Sent to Loggly FAIL : " + body.__str__() + " error = " + content.__str__()
        #    print msg
        #    syslog.syslog(msg)        
        
        # crude form of rate-limiter
        #time.sleep(0.2)
        
        # Return the JSON structure so it can be used by NoSQL type databases
        sdata = json.dumps(sdata)
        pprint(sdata)
        #writeToSyslogFake(sdata)
        return sdata
                                         
    except Exception,e:
        msg = "kojoney_loggly.py : sendToLoggly() : exception : " + e.__str__() + " line=" + line
        print msg
        syslog.syslog(msg)
        return None
        
# -------------------------------------------------------
# Start of code
        
if __name__ == '__main__' :
       
    # Set the input file to scan
    filename = '/var/log/messages'
    filename = 'botjuicer.log'		# grep out from tweet_queue.log
    filename = '/home/var/log/tweet_queue.log'

    sensorId = "IGNORE"
        
    file = open(filename,'r')
    
    while True:
        # Tweets log file       
        # where = file.tell()
        line = file.readline()
        line = line.rstrip('\n')
        if "tweet=" in line:
            line = line.split("tweet=")[1]
        
        if not line:		# no data to process
            pass
        else :			# new data has been found
            #if "SNORT_NIDS" not in line:				# for testing only
            #if "IPLOG" not in line:					# for testing only
            #if "WEB" not in line:					# for testing only
            #if "BOTJUICER" not in line:				# for testing only
            #if "CLAMD" not in line:					# for testing only
            #if "REPORT" not in line or "flags={" not in line :		# for testing only
            #if "ANALYST,AV" not in line :				# for testing only            
            #    continue
            
            sdata = sendToLoggly(sensorID,line)
                       
        time.sleep(0.5)		# 0.1 
                              
                 