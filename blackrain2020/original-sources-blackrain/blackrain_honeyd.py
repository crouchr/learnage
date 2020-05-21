#!/usr/local/bin/python

# NO
# --
#2011-06-02-22:56:01.9319 honeyd log started ------
#2011-06-02-22:56:15.4702 honeyd log stopped ------
#2011-06-02-22:58:32.9769 honeyd log started ------
#2011-06-02-22:58:45.7338 tcp(6) S 192.168.1.248 39997 192.168.1.150 445 [Linux 2.6 .1-7]
#2011-06-02-22:58:51.0419 tcp(6) E 192.168.1.248 39997 192.168.1.150 445: 17 0
#2011-06-02-23:00:07.8425 icmp(1) - 192.168.1.248 192.168.1.150: 8(0): 84 [Linux 2.6 .1-7]
#2011-06-02-23:00:08.8410 icmp(1) - 192.168.1.248 192.168.1.150: 8(0): 84 [Linux 2.6 .1-7]
#2011-06-02-23:00:09.8378 icmp(1) - 192.168.1.248 192.168.1.150: 8(0): 84 [Linux 2.6 .1-7]
#2011-06-02-23:00:10.8387 icmp(1) - 192.168.1.248 192.168.1.150: 8(0): 84 [Linux 2.6 .1-7]
#2011-06-02-23:00:11.8884 icmp(1) - 192.168.1.248 192.168.1.150: 8(0): 84 [Linux 2.6 .1-7]
#2011-06-02-23:00:27.0663 tcp(6) S 192.168.1.248 38744 192.168.1.150 445 [Linux 2.6 .1-7]
#2011-06-02-23:00:40.9598 tcp(6) E 192.168.1.248 38744 192.168.1.150 445: 24 0


# YES
# ---
#Jul 19 22:37:08 mars honeyd[2924]: 2011-07-19:22-37-08:tcp(6):START:218.200.37.155 6000 192.168.1.63 1433:genre=Novell:NetWare 5.0:hops=33:linktype=ethernet/modem:tos=0:uptime(hrs)=?:masq-score=0% (flags 0):firewall=yes:NAT=yes:realOS=1:
#Jul 19 22:37:09 mars honeyd[2924]: 2011-07-19:22-37-09:tcp(6):END:218.200.37.155 6000 192.168.1.63 1433:rx=0:tx=0:
#Jul 19 22:37:27 mars honeyd[2924]: 2011-07-19:22-37-27:tcp(6):START:218.200.37.155 5228 192.168.1.63 1433:genre=Windows:2000 SP4, XP SP1+:hops=25:linktype=ethernet/modem:tos=0:uptime(hrs)=?:masq-score=8% (flags 20b):firewall=no:NAT=yes:realOS=1:
#Jul 19 22:37:43 mars honeyd[2924]: 2011-07-19:22-37-43:tcp(6):END:218.200.37.155 5228 192.168.1.63 1433:rx=158:tx=0:
#Jul 19 22:37:48 mars honeyd[2924]: arp reply 192.168.1.63 is-at 00:04:23:a5:b0:f3
#Jul 19 22:54:25 mars honeyd[2924]: arp reply 192.168.1.63 is-at 00:04:23:a5:b0:f3
#Jul 19 22:54:25 mars honeyd[2924]: 2011-07-19:22-54-25:tcp(6):PROBE:182.50.135.1 80 192.168.1.63 20736:44: SA:Error=p0f did not find a match:
#Jul 19 22:58:44 mars honeyd[2924]: arp reply 192.168.1.63 is-at 00:04:23:a5:b0:f3
#Jul 19 22:58:44 mars honeyd[2924]: 2011-07-19:22-58-44:tcp(6):PROBE:182.50.135.1 80 192.168.1.63 20736:44: SA:Error=p0f did not find a match:
#Jul 19 23:00:26 mars honeyd[2924]: 2011-07-19:23-00-26:tcp(6):PROBE:182.50.135.1 80 192.168.1.63 20736:44: SA:Error=p0f did not find a match:
#Jul 19 23:00:31 mars honeyd[2924]: arp reply 192.168.1.63 is-at 00:04:23:a5:b0:f3
#Jul 19 23:12:08 mars honeyd[2924]: arp reply 192.168.1.63 is-at 00:04:23:a5:b0:f3
#Jul 19 23:12:08 mars honeyd[2924]: 2011-07-19:23-12-08:tcp(6):PROBE:182.50.135.1 80 192.168.1.63 20736:44: SA:Error=p0f did not find a match:
#Jul 19 23:16:11 mars honeyd[2924]: 2011-07-19:23-16-11:tcp(6):PROBE:182.50.135.1 80 192.168.1.63 20736:44: SA:Error=p0f did not find a match:
#Jul 19 23:16:16 mars honeyd[2924]: arp reply 192.168.1.63 is-at 00:04:23:a5:b0:f3
#Jul 19 23:47:05 mars honeyd[2924]: arp reply 192.168.1.63 is-at 00:04:23:a5:b0:f3
#Jul 19 23:47:05 mars honeyd[2924]: 2011-07-19:23-47-05:tcp(6):PROBE:182.50.135.1 80 192.168.1.63 20736:44: SA:Error=p0f did not find a match:

import re
import syslog
import ipintellib

def processHoneyd(line):
    flowEvent = {}
    
    try : 
        #print "\nEntered blackrain_honeyd.processHoneyd()"
        #print line
                
        flowEvent['flowType'] = "FLOW_HONEYD_FLOW"
        
        ip = re.findall("\d+\.\d+\.\d+\.\d+",line) 
        if len(ip) == 0 :
            #print "No IP addresses found"
            return None
        #else :
        #    print "Found IP addresses..."
            
        if not "END" in line:
            #print "No END honeyd flow found, so return None"
            return None
            
        sIP = re.findall("(\d+\.\d+\.\d+\.\d+)",line)[0] 
        #print sIP
        
        sP  = re.findall("\d+\.\d+\.\d+\.\d+ (\d+) \d+\.\d+\.\d+\.\d+ \d+",line)[0] 
        #print sP
         
        dP  = re.findall("\d+\.\d+\.\d+\.\d+ \d+ \d+\.\d+\.\d+\.\d+ (\d+)",line)[0] 
        #print dP
        
        flowEvent['flowDirection']  = "in"
        flowEvent['flowRemoteIP']   = sIP 
        flowEvent['flowRemotePort'] = sP 
        flowEvent['flowHpotPort']   = dP

        if "icmp" in line:
            flowEvent['flowProto'] = "I"
        elif "tcp" in line:
            flowEvent['flowProto'] = "T"
        elif "udp" in line:
            flowEvent['flowProto'] = "UDP"
        else:
            flowEvent['flowProto'] = "unknown"	# attention : need to test other protocols
            
        #flowEvent['flowOS']    = "none"

        # Optional parameters 
        # ===================   
        #flowEvent['flowDuration']  
        #flowEvent['flowPkts'] 
        #flowEvent['flowTflags']   = re.findall("fl=(\d+)",line)[0] 
         
        # Number of bytes received by the honeypot
        # This does not include the data part of the TCP handshake
        flowEvent['flowBytes']    = re.findall("rx=(\d+)",line)[0]   
        
        #print flowEvent
        
        # Data enrichment
        # ===============
        # DNS info
        dnsInfo = ipintellib.ip2name(flowEvent['flowRemoteIP'])
        flowEvent['flowDNS'] = dnsInfo['name'].rstrip('.')   
        #print flowEvent['flowDNS']
        
        # GeoIP info
        geoIP = ipintellib.geo_ip(flowEvent['flowRemoteIP'])
        flowEvent['flowCC']      = geoIP['countryCode']      
        flowEvent['flowCountry'] = geoIP['countryName']     
        flowEvent['flowCity']    = geoIP['city']
        flowEvent['flowLat' ]    = "%.3f" % float(geoIP['latitude'])                          
        flowEvent['flowLong' ]   = "%.3f" % float(geoIP['longitude'])                         
        #print flowEvent['flowCC']
        
        # WHOIS info        
        asInfo = ipintellib.ip2asn(flowEvent['flowRemoteIP'])
        flowEvent['flowASN']    = asInfo['as']   		       		# AS123   
        flowEvent['flowISP']    = asInfo['registeredCode']		     	# Short-form e.g. LEVEL3
        flowEvent['flowRoute']  = asInfo['netblock']	
        flowEvent['flowRIR']    = asInfo['registry']	
        #print flowEvent['flowASN']                                                                  
        
        #print flowEvent
        return flowEvent
            
    except Exception,e :
        msg = "Exception : " + e.__str__() + " in line=" + line
        print msg
        syslog.syslog(msg)
        return None

#if __name__ == '__main__' :
    #line = "Jul 10 19:29:28 mars honeyd[2854]: 2011-07-10:19-29-28:tcp(6):END:70.60.14.52 2247 192.168.1.63 9988:rx=67584:tx=0:"
    #print processHoneyd(line)
    #
    #line = "2011-06-02-22:56:01.9319 honeyd log started ------"
    #print processHoneyd(line)
    #
    #line = "2011-06-02-22:56:15.4702 honeyd log stopped ------"
    #print processHoneyd(line)
    #
    #line = "2011-06-02-22:58:32.9769 honeyd log started ------"
    #print processHoneyd(line)
    #
    #line = "2011-06-02-22:58:45.7338 tcp(6) S 192.168.1.248 39997 192.168.1.150 445 [Linux 2.6 .1-7]"
    #print processHoneyd(line)
    
#    line = "2011-06-02-22:58:51.0419 tcp(6) E 3.3.3.3 39997 192.168.1.150 445: 17 0"
#    print processHoneyd(line)
#    
#    line = "2011-06-02-23:00:07.8425 icmp(1) - 192.168.1.248 192.168.1.150: 8(0): 84 [Linux 2.6 .1-7]"
#    print processHoneyd(line)
#    
#    line = "2011-06-02-23:00:08.8410 icmp(1) - 192.168.1.248 192.168.1.150: 8(0): 84 [Linux 2.6 .1-7]"
#    print processHoneyd(line)
#    
#    line = "2011-06-02-23:00:09.8378 icmp(1) - 192.168.1.248 192.168.1.150: 8(0): 84 [Linux 2.6 .1-7]"
#    print processHoneyd(line)
    