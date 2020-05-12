#!/usr/bin/python

import syslog
import kojoney_bitly
import getURLghetto

BRX_IP = "192.168.1.90"				# bug : read from a file in future

# add exception handling !!!
# works for Snort and Suricata
def suricataTwittify(tweet):

    #print "kojoney_suricata_parse.py : suricataTwittify() : before twittification, raw tweet = " + tweet
                        
    tweet = tweet.replace("mars snort","")	# Snort-specific
    tweet = tweet.replace("mars suricata","")	# Suricata-specific
                                        
    tweet = tweet.replace("Classification: ","CL:")
    tweet = tweet.replace("Priority: ","PR:")
    tweet = tweet.replace("[PR:1]","P1")
    tweet = tweet.replace("[PR:2]","P2")
    tweet = tweet.replace("[PR:3]","P3")
                                                                            
    tweet = tweet.replace("ET SCAN ","")
    tweet = tweet.replace("ET COMPROMISED ","")
    tweet = tweet.replace("ET DROP ","")   
    tweet = tweet.replace("ET ATTACK_RESPONSE ","")
    tweet = tweet.replace("ET EXPLOIT ","")
    tweet = tweet.replace("ET RBN ","")    
    tweet = tweet.replace("ET MALWARE ","")
    tweet = tweet.replace("ET USER_AGENTS ","")
    tweet = tweet.replace("ET POLICY ","")
    tweet = tweet.replace("ET WEB_SERVER ","")
    tweet = tweet.replace("ET WEB_SPECIFIC_APPS ","")
    tweet = tweet.replace("ET P2P ","")
    tweet = tweet.replace("GPL POLICY ","") 
    tweet = tweet.replace("GPL EXPLOIT ","") 
                                                                                                                
    # Snort - protocol normalisation        
    tweet = tweet.replace("{TCP}" ,"T")
    tweet = tweet.replace("{ICMP}","I")
    tweet = tweet.replace("{UDP}" ,"U")
    tweet = tweet.replace("{6}"   ,"T")
    tweet = tweet.replace("{1}"   ,"I")
    tweet = tweet.replace("{17}"  ,"U")
                                                                                                                                              
    tweet = tweet.replace(" -> ","->")
    #tweet = tweet.replace("[Xref => ","xrf=")
    tweet = tweet.replace("[**] ","")
                                                                                                                                                                      
    # Obfuscate honeypot IPs - this is common to all events so needs to be broken out                                                                                                                                                                                  
    tweet = tweet.replace("172.31.0.67" ,  "LINUX"  )             # High-interaction    Linux   honeypot
    tweet = tweet.replace("192.168.1.66",  "AMUN"   )             # Medium-interaction  Linux   honeypot
    tweet = tweet.replace("192.168.1.65",  "NEP"    )             # Medium-interaction  Win32   honeypot
    tweet = tweet.replace("192.168.1.64",  "KIPPO"  )             # Medium-interaction  SSH     honeypot
    tweet = tweet.replace("192.168.1.63",  "HONEYD" )             # Low-interaction     generic honeypot
    tweet = tweet.replace("192.168.1.62",  "WEB"    )             # Glastopf
    tweet = tweet.replace("192.168.1.61",  "SMTP"   )             # Port 25 SPAM
    tweet = tweet.replace("192.168.1.60",  "HTRAP"  )             # Honeytrap 
    tweet = tweet.replace("192.168.1.67",  "BRAIN"  )             # The botwall / mars node
    tweet = tweet.replace("192.168.1.131", "ASTRX"  )             # Asterisk
    tweet = tweet.replace("192.168.1.7",   "BG"     )             # Border (of Honeynet) Gateway router
    tweet = tweet.replace("192.168.1.254", "ADSL"   )             # WRT DSL router to Internet
    
    # Shorten common Snort alerts
    tweet = tweet.replace("Known Compromised or Hostile Host Traffic","Hostile host")
    tweet = tweet.replace("Known Russian Business Network IP","RBN host")
    tweet = tweet.replace("Dshield Block Listed Source","DSHIELD host")  
    tweet = tweet.replace("Known Bot C&C Server Traffic","Botnet C&C host")
                        
    tweet = tweet.replace("Executable code was detected","Code")
    tweet = tweet.replace("Code detected","Code")
    tweet = tweet.replace("xor Decoder Code","Code")
    tweet = tweet.replace("SHELLCODE","Code")
    tweet = tweet.replace("Shellcode","Code")
                                                
    tweet = tweet.replace("(ftp_telnet)","")
                                                        
    tweet = tweet.replace("Attempted Information Leak","LEAK")
    tweet = tweet.replace("FTP bounce attempt","FTP bounce ")   # also fixes missing space in Snort message ?
    tweet = tweet.replace("MS Terminal server request ","MS T-Server req. ")
    
    tweet = tweet.replace("RDP connection request","MS RDP conn. req.")
    tweet = tweet.replace("RDP attempted administrator connection request","MS RDP conn. req.")
    tweet = tweet.replace("Radmin Remote Control Session Setup Initiate","Radmin session")
    tweet = tweet.replace("Remote Desktop Administrator Login Request","RDP Login Request")
    
    tweet = tweet.replace("Suspicious ingress to MSSQL port 1433","MSSQL traffic")
    tweet = tweet.replace("Filtered Portsweep","Portsweep")
    tweet = tweet.replace("TCP Portsweep","TCP Portsweep ")     # is there a bug in the Snort signature ? - no trailing space so add one here
    
    tweet = tweet.replace("Sipvicious User-Agent Detected","SIPvicious scan")
    tweet = tweet.replace("Sipvicious detected","SIPvicious scan")
    tweet = tweet.replace("Sipvicious tool (friendly-scanner)","SIPvicious scan")
    tweet = tweet.replace("Sipvicious tool (sundayddr)","SIPvicious scan")
    tweet = tweet.replace("Modified Sipvicious Sundayddr Scanner","Modified SIPvicious Sundayddr scan")
    tweet = tweet.replace("(friendly-scanner)","(friendly)")
    
    # Cisco
    tweet = tweet.replace("Cisco Device New Config Built", "Cisco config saved" )
    tweet = tweet.replace("Cisco Device in Config Mode"  , "Cisco conf t action")    
    
    tweet = tweet.replace("Tomcat Web Application Manager scanning","Tomcat WAM scan")
    
    # ICMP
    tweet = tweet.replace("ICMP Destination Unreachable Fragmentation Needed and DF bit was set","ICMP Unreachable : DF bit set")
    tweet = tweet.replace("ICMP Destination Unreachable Port Unreachable","ICMP Unreachable : port")
    
    tweet = tweet.replace("RemoteCreateInstance attempt","RCI")					# Snort : 3397
    tweet = tweet.replace("DsRolerGetPrimaryDomainInformation attempt","DsGetDomain attempt")	# Snort : 5095
    tweet = tweet.replace("NetrPathCanonicalize overflow attempt","NetrPath oflow")		# Snort : 7209
    tweet = tweet.replace("NETBIOS DCERPC NCACN-IP-TCP","NetBIOS")				# Snort : 7209
    tweet = tweet.replace("NETBIOS RPC exploit","NetBIOS exploit")
    tweet = tweet.replace("NETBIOS SMB-DS Trans unicode Max Param DOS attempt","NetBIOS Max Param DoS exploit")	# snort 5731
    tweet = tweet.replace("symantec antivirus realtime virusscan overflow attempt","Symantec o/flow")
    tweet = tweet.replace("Symantec Remote Management RTVScan Exploit","Symantec o/flow")
    tweet = tweet.replace("Suspicious ingress to Oracle SQL port 1521","Oracle SQL scan")
    tweet = tweet.replace("Attempted Administrator Privilege Gain","Escalation attempt") 
    tweet = tweet.replace("ASN.1 constructed bit string","ASN.1 bit string") 
    tweet = tweet.replace("Successfull Administrator Privilege Gain", "Escalated to Admin")
    tweet = tweet.replace("Successful Administrator Privilege Gain" , "Escalated to Admin") 
    tweet = tweet.replace("Possible MS CMD Shell opened on local system","cmd.exe") 
    tweet = tweet.replace("Edonkey Search Results","eDonkey search") 
    tweet = tweet.replace("SOCKSv4 HTTP Proxy Inbound Request","SOCKSv4 HTTP Request")		# Snort 2003262
    tweet = tweet.replace("DNS Windows NAT helper components tcp denial of service attempt","DNS Windows NAT DoS attempt")	# Snort 8709
    tweet = tweet.replace("SQL Worm propagation attempt","SQL worm")
    tweet = tweet.replace("SQL version overflow attempt","SQL worm")
    
    tweet = tweet.replace("NMAP","Nmap")
    tweet = tweet.replace("SPECIFIC-THREATS","")
    
    tweet = tweet.replace("LibSSH Based Frequent SSH Connections Likely BruteForce Attack!","SSH bruteforce attack");
    tweet = tweet.replace("Rapid POP3 Connections - Possible Brute Force Attack","POP3 bruteforce attack");
                                                                                                                                                        
    tweet = tweet.replace("A Network Trojan was detected","Trojan")
    tweet = tweet.replace("Internet Explorer","IE")
    tweet = tweet.replace("Microsoft","")
    tweet = tweet.replace("access to a potentially vulnerable web application","Web app exploit")
    tweet = tweet.replace("DCERPC rpcmgmt ifids Unauthenticated BIND","NETBIOS RPC exploit")
    
    # Shorten snort attack classification type
    tweet = tweet.replace("Misc Attack","MISC")
    tweet = tweet.replace("Potential Corporate Privacy Violation","PRIV") 
    tweet = tweet.replace("Privacy violation","PRIV")
    tweet = tweet.replace("Misc activity","MISC")
    tweet = tweet.replace("Potentially Bad Traffic","BAD_TRAF")
    tweet = tweet.replace("Detection of a Network Scan","SCAN")   
    tweet = tweet.replace("Escalation attempt","ESCLN")
    tweet = tweet.replace("Escalated to Admin","ESCLN")
    tweet = tweet.replace("ATTACK-RESPONSES","RESPONSE")
    tweet = tweet.replace("Detection of a non-standard protocol or event","NON-STD")
    tweet = tweet.replace("Generic Protocol Command Decode","CMD")
    tweet = tweet.replace("Web Application Attack","WEB_APP")
    tweet = tweet.replace("Web app exploit","WEB_APP")
    tweet = tweet.replace("Attempted Denial of Service","DOX")	# seen with SIP REGISTER messages
                                    
                                    
    # PHP                                
    tweet = tweet.replace("(monster list http)",   "")     # PHP RFI
    tweet = tweet.replace("Remote File Inclusion", "RFI")  # PHP RFI
    
    # Miscellaneous
    tweet = tweet.replace("Suspicious", "Suspc."  )
    tweet = tweet.replace("inbound" ,   "ingress" )          # traffic direction normalisation
    tweet = tweet.replace("outbound",   "egress"  )          # traffic direction normalisation
                                                        
    #print "kojoney_surcata_parse.py : twittifySuricata() : after twittification, tweet = " + tweet
                                                                
    return tweet                                                                                                                                                                                                                                         
                                                                                                                                                                                 
                                                                                                                                                                                                          

# does this break if there is not an Xref in the alert ?
def processSur(line):
  
    try:
        shorturl=""
        
        line = line.rstrip("\n")
        if line.find("NIDS_SU") == -1 :
            return
                                                                                
        # !!! : proper way is to do the filtering in suricata config - do it here for the  moment            

        # drop IDS events related to traffic to the BRX node
        if line.find(BRX_IP) != -1 :
            #msg = "Following IDS event is related to BRX node so ignore : " + line
            #print msg
            #syslog.syslog("kojoney_suricata_parse.py : processSur() : " + msg)
            return
                                                                                
        # drop uninteresting events
        if line.find(":2010937:") != -1:
            return
        
        if line.find(":368:") != -1 :			# ICMP ping - asteris and HP laptop running botwall
            return
        
        if line.find(":396:") != -1 :			# ICMP unreachable : DF set
            return

        if line.find(":402:") != -1 :			# ICMP unreachable : port
            return					# my traceroute-matrix.py triggers false alarms
            
        #if line.find(":2010935:") != -1:                # mssql tcp 1433 is frequent
        #    return
        
        if line.find(":2008052:") != -1:                # kludge : suspicious user agent - this is triggered by Anubis or cwsandbox
            return					# need to add check that dest IP is one of these and only then drop the message
        
        if line.find(":2013031:") != -1:                # outgoing messages to Twitter are triggering false alarms
            return					
 
        if line.find(":2003068:") != -1:                # outbound nmap scanning triggers this
            return					

        if line.find(":2013031:") != -1:                # python urlib - used to communicate to BRX - false positive
            return					
                                                                                                                                        
        # 2 identical alerts for same signature
        if line.find(":1448:") != -1:                   # MS terminal server tcp 3389
            return  
        
        # 2 identical alerts for same signature
        if line.find(":4060:") != -1:                   # MS terminal server tcp 3389
            return  
        
        # 2 identical alerts for same signature
        if line.find(":2123:") != -1:                   # Successful Admin gain - drop the GPL one
            return  
        
        # POP3 brute force attack - just blows out Twitter API without correlation
        # re-instated now that Twitter feed has correlation
        #if line.find(":2011124:") != -1:                   
        #    return  
        
        # Symantec exploit - this is a duplicate of an ET signature
        if line.find(":6512:") != -1:                   
            return  
                                                                                                                                                   
        line   = line.rstrip('\n')       
        
        # strip off date and unwanted syslog pre-messages
        fields = line.split(":")
        #print fields
        line = ':'.join(fields[3:])
        line = line.lstrip()	# strip leading space
        #print line
        
        # strip off trailing (possibly multiple) Xref
        fields = line.split("=>")                                                    
        #print line
        #print fields
        
        #if len(fields) > 1:
        a = fields[1]
        b = a.split('[')[0]
        b = b.strip(']')
        
        longUrl = getURLghetto.getURLghetto(b)
        #print "longUrl  = " + longUrl
        shortUrl = kojoney_bitly.getBitly(longUrl)
        #print "shortUrl = " + shortUrl        
        
        # Extract all parts of the alert before the Xref=> parts
        a = line.replace("[Xref","@");
        #print a
        b = a.split('@')
        c = b[0] 
        c = c.replace("[**] ","")
        c = c.replace("  "," ")		# double space to single spaces
        tweet = c + "xrf " + shortUrl	# allow space around URL for iPhone to pick out as a URL  
        
        tweet = suricataTwittify(tweet)
        return tweet
        
    except Exception,e:
        syslog.syslog("kojoney_suricata_parsey.py : breakdownSuricataAlert() : " + `e` + " line=" + line)
                

if __name__ == '__main__' :
    
    filename = '/home/var/log/suricata.syslog'
    file = open(filename,'r')
                
    while True:
        line  = file.readline() 
        tweet = processSur(line)
        
        if tweet != None:
            print "tweet:" + tweet
        
        