#!/usr/bin/python

import time, os , syslog , re 
import httplib2
import ipintellib
import simplejson as json

# Loggly : User account honeypotr@honeytweeter : pass = fuckloggly99 / email = uber.koob@gmail.com

txnId = 0

# process a Tweet Queue message and submit to Loggly LaaS
def sendToLoggly(sensorId,line):
    
    try :
        global txnId                    
        
        print "sendToLoggly() : line=" + line
        
        # honeytweeter
        #shakey = "e25e6042-e490-4910-a246-94cefbdd11b9"               
        
        # honeytweeter-json
        shakey = "fe39eb54-7c8f-417c-afc8-5b8db98961d3"               

        sdata = {}

        # Event Type
        fields = line.split(",")
        eventType = fields[0]
        sdata['eventType'] = fields[0]
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
            
            # Reverse DNS
            dnsInfo = ipintellib.ip2name(sdata['ip'])
            dnsName = dnsInfo['name']
            if dnsName != "NoDNS":
                sdata['rdns'] = dnsName.rstrip('.')            
        
            # ASN info
            asInfo = ipintellib.ip2asn(sdata['ip']) 
            asNum = asInfo['as']                                                # AS123   
            asRegisteredCode = asInfo['registeredCode'].upper()                 # e.g. GOOGLE
            sdata['asn'] = "AS" + asNum
            sdata['isp'] = asRegisteredCode                           

        # Snort SID
        if sdata['eventType'] == "SNORT_NIDS" :
            sids = re.findall("SID=(\d+)",line)
            if len(sids) > 0:
                sdata['sid'] = sids[0]
            a = re.findall("P(\d+) SID",line)
            if len(a) > 0 :
                sdata['priority'] = "P" + a[0]
        
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
            
        # Destination port    
        # ----------------
        # Snort messages
        flow = re.findall("\w+\:(\d+) ",line)    
        if len(flow) > 0 :
            sdata['port'] = int(flow[0])    
        
        # IPLOG    
        if sdata['eventType'] == "IPLOG" :
           ports = re.findall("port (\d+)",line)    
           if len(ports) > 0 :
               sdata['port'] = int(ports[0])

        # CLAMD - clsniffer    
        if sdata['eventType'] == "CLAMD" :
           ports = re.findall("d=(\d+)",line)    
           if len(ports) > 0 :
               sdata['port'] = int(ports[0])
        
        # KIPPO
        if sdata['eventType'] == "KIPPO" :
            sdata['port'] = 2222
            sdata['protocol'] = "tcp"
        
        # Glastopf       
        if "WEB" in sdata['eventType'] :
            sdata['port'] = 18080    
            sdata['protocol'] = "tcp"       
        
        # Botjuicer cracked scripts
        if sdata['eventType'] == "ANALYST" and "BOTJUICER" in line :
            #if "UNDETERMINED" in line.upper():
            #    return None
            #print "BOTJUICER log found : " + line
            a = re.findall("p=(\d+)",line)
            if len(a) > 0 : 
                sdata['port'] = int(a[0])
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
        sdata['msg'] = line
        
        # Txnid - increment this last, just before submission to Loggly
        txnId = txnId + 1
        sdata['txnId'] = txnId
                
        body = json.dumps(sdata)        
        
        print "sendToLoggly() : JSON body = " + body
                         
        # Send to Loggly
                         
        insert_url = "http://logs.loggly.com/inputs/" + shakey
        insert_http = httplib2.Http(timeout=10)
        #body = line
        resp, content = insert_http.request(insert_url, "POST", body=body, headers={'content-type':'text/plain'})
        #print "Loggly : resp : " + resp.__str__()
        #print "Loggly : content : " + content.__str__()             
        
        #{'status': '200', 'content-length': '18', 'vary': 'Accept-Encoding', 'server': 'TwistedWeb/12.0.0', 'date': 'Tue, 25 Jun 2013 05:55:58 GMT', 'content-type': 'text/html'}
        #{"response": "ok"}
        
        if "ok" in content.__str__() :		# bug -> why can't I look at the "response" field in a structured way
            msg = "Sent to Loggly OK : " + body.__str__()
            print msg
        else:
            msg = "Sent to Loggly FAIL : " + body.__str__() + " error = " + content.__str__()
            print msg
            syslog.syslog(msg)        
        
        # crude form of rate-limiter
        time.sleep(0.5)
                                 
    except Exception,e:
        msg = "kojoney_loggly.py : sendToLoggly() : exception : " + e.__str__() + " line=" + line
        print msg
        syslog.syslog(msg)
        
                               
# -------------------------------------------------------

        
# Start of code
# This is a test harness so comment/uncomment the relevent lines        
# bug : sensorId and name are not yet used
        
if __name__ == '__main__' :
       
    # Set the input file to scan
    filename = '/var/log/messages'
    filename = 'botjuicer.log'		# grep out from tweet_queue.log
    
    filename = '/home/var/log/tweet_queue.log'
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
            #if "SNORT_NIDS" not in line:	# for testing only
            #if "IPLOG" not in line:		# for testing only
            #if "WEB" not in line:		# for testing only
            #if "BOTJUICER" not in line:	# for testing only
            #if "CLAMD" not in line:		# for testing only
            #if "REPORT" not in line or "flags={" not in line :		# for testing only
            if "ANALYST,AV" not in line :		# for testing only            
                continue
                
            msg = sendToLoggly("TEST",line)
                       
        #print "sleeping..."
        # this can be a float for sub-second sleep    
        time.sleep(0.1)		# 0.1 
                              
                 