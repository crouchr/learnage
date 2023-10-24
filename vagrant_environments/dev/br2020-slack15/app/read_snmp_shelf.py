#!/usr/bin/python


import time
import sys
#import os , syslog , re 
#import kojoney_funcs
import ipintellib
#import twitter_funcs
#import kojoney_correlate
import shelve



# Update shelved object with SNMP stats in it                                   
def printAttackerOIDs():    
    # need to add logic to fail if the shelf file does not exist
    database = shelve.open('/home/var/log/attacker_shelf.dat')
    if len(database) == 0 :		# contains no entries
        sys.exit("Failed to locate shelf file")
    
    print " "        
    
    print "Attackers"
    print "---------"
    print "NUM_IP              : " + database['NUM_IP'].__str__()
    print "NUM_SLASH_24        : " + database['NUM_SLASH_24'].__str__() 
    print "NUM_CC              : " + database['NUM_CC'].__str__()
    print "NUM_CITY            : " + database['NUM_CITY'].__str__()
    print "NUM_ASN             : " + database['NUM_ASN'].__str__()
    print " "
    print "Malware Captured"
    print "----------------"
    print "AMUN_FILES_BIN      : " + database['AMUN_FILES_BIN'].__str__()
    print "AMUN_FILES_HEX      : " + database['AMUN_FILES_HEX'].__str__()
    print "NEPENTHES_FILES     : " + database['NEPENTHES_FILES'].__str__()
    print "KIPPO_FILES         : " + database['KIPPO_FILES'].__str__()
    print "GLASTOPF_FILES_GET  : " + database['GLASTOPF_FILES_GET'].__str__()
    print "GLASTOPF_FILES_POST : " + database['GLASTOPF_FILES_POST'].__str__()
    print "ANALYST_FILES_ALL   : " + database['ANALYST_FILES_ALL'].__str__()
    print "ANALYST_FILES_EXE   : " + database['ANALYST_FILES_EXE'].__str__()
    print "ANALYST_FILES_PHP   : " + database['ANALYST_FILES_PHP'].__str__()
    print "ANALYST_FILES_TXT   : " + database['ANALYST_FILES_TXT'].__str__()
    print "ANALYST_FILES_GIF   : " + database['ANALYST_FILES_GIF'].__str__()
    print "ANALYST_FILES_JPG   : " + database['ANALYST_FILES_JPG'].__str__()
    print "ANALYST_FILES_PNG   : " + database['ANALYST_FILES_PNG'].__str__()
    print "ANALYST_FILES_TGZ   : " + database['ANALYST_FILES_TGZ'].__str__()

    print " "
    print "Attackers"
    
    outfile = "blackrain_attackers-report.csv"
    fp = open(outfile,'w')
    
    for ip in database['IP'] :
        asInfo = ipintellib.ip2asn(ip)                               # 
        asNum = asInfo['as']                                           # AS123   
        asRegisteredCode = asInfo['registeredCode']                     # Short-form e.g.ARCOR        

        geoIP = ipintellib.geo_ip(ip)                                
        countryCode = geoIP['countryCode']                              
        city        = geoIP['city']
        longitude   = geoIP['longitude']                                # Used to calc approx. localtime
        latitude    = geoIP['latitude']    

        dnsInfo = ipintellib.ip2name(ip)
        dnsName = dnsInfo['name'].rstrip('.')     
        
        msg = ip + "," + "AS" + asNum.__str__() + "," + countryCode + "," + dnsName.__str__() + "," + asRegisteredCode.__str__() + "," + countryCode.__str__() + "," + city.__str__() 
        
        print msg
        print >> fp,msg
    
    fp.close()
    #print "NUM_SLASH_24        : " + database['NUM_SLASH_24'].__str__() 
    #print "NUM_CC              : " + database['NUM_CC'].__str__()
    #print "NUM_CITY            : " + database['NUM_CITY'].__str__()
    #print "NUM_ASN             : " + database['NUM_ASN'].__str__()


           
# Update shelved object with SNMP stats in it                                   
def printSnmpOIDs():
    
    # need to add logic to fail if the shelf file does not exist
    database = shelve.open('/home/var/log/snmp_shelf.dat')
    if len(database) == 0 :		# contains no entries
        sys.exit("Failed to locate shelf file")
    
    print " "        
    
    print "Netflow"
    print "-------"
    print "NETFLOW_IN           : " + database['NETFLOW_IN'].__str__()
    print "NETFLOW_OUT          : " + database['NETFLOW_OUT'].__str__()
    print "NETFLOW_TFTP         : " + database['NETFLOW_TFTP'].__str__()
    print "NETFLOW_HTTP         : " + database['NETFLOW_HTTP'].__str__()
    print "NETFLOW_OTHER        : " + database['NETFLOW_OTHER'].__str__()
    print "NETFLOW_TROJAN       : " + database['NETFLOW_TROJAN'].__str__()
    print "NETFLOW_HTTP_18080   : " + database['NETFLOW_HTTP_18080'].__str__()
    print "NETFLOW_HTTP_8080    : " + database['NETFLOW_HTTP_8080'].__str__()
    print "NETFLOW_HTTP_3128    : " + database['NETFLOW_HTTP_3128'].__str__()
    print "NETFLOW_HTTPS        : " + database['NETFLOW_HTTPS'].__str__()
    print "NETFLOW_SSH          : " + database['NETFLOW_SSH'].__str__()
    print "NETFLOW_SSH_2222     : " + database['NETFLOW_SSH_2222'].__str__()
    print "NETFLOW_TELNET       : " + database['NETFLOW_TELNET'].__str__()
    print "NETFLOW_445          : " + database['NETFLOW_445'].__str__()
    print "NETFLOW_135          : " + database['NETFLOW_135'].__str__()
    print "NETFLOW_137          : " + database['NETFLOW_137'].__str__()
    print "NETFLOW_138          : " + database['NETFLOW_138'].__str__()
    print "NETFLOW_139          : " + database['NETFLOW_139'].__str__()
    print "NETFLOW_SNMP         : " + database['NETFLOW_SNMP'].__str__()
    print "NETFLOW_SIP          : " + database['NETFLOW_SIP'].__str__()
    print "NETFLOW_DNS          : " + database['NETFLOW_DNS'].__str__()
    print "NETFLOW_RDP          : " + database['NETFLOW_RDP'].__str__()
    print "NETFLOW_IDENT        : " + database['NETFLOW_IDENT'].__str__()
    print "NETFLOW_FINGER       : " + database['NETFLOW_FINGER'].__str__()
    print "NETFLOW_POP3         : " + database['NETFLOW_POP3'].__str__()
    print "NETFLOW_IRCD         : " + database['NETFLOW_IRCD'].__str__()
    print "NETFLOW_VNC          : " + database['NETFLOW_VNC'].__str__()
    print "NETFLOW_PPTP         : " + database['NETFLOW_PPTP'].__str__()
    print "NETFLOW_SMTP         : " + database['NETFLOW_SMTP'].__str__()
    print "NETFLOW_FTP_CONTROL  : " + database['NETFLOW_FTP_CONTROL'].__str__()
    print "NETFLOW_FTP_DATA     : " + database['NETFLOW_FTP_DATA'].__str__()
    print "NETFLOW_FTP_CONTROL  : " + database['NETFLOW_FTP_CONTROL'].__str__()
    print "NETFLOW_TELNET_10023 : " + database['NETFLOW_TELNET_10023'].__str__()
    print "NETFLOW_SMTP_10025   : " + database['NETFLOW_SMTP_10025'].__str__()
    print " "
    print "Web Honeypot"
    print "------------"
    print "WEB_SCAN         : " + database['WEB_SCAN'].__str__()
    print "WEB_X_GET        : " + database['WEB_X_GET'].__str__()
    print "WEB_X_POST       : " + database['WEB_X_POST'].__str__()
    print "WEB_PRX          : " + database['WEB_PRX'].__str__()
    print "WEB_OPEN         : " + database['WEB_OPEN'].__str__()
    print "WEB_WRITE        : " + database['WEB_WRITE'].__str__()
    print " "
    print "Win32 Honeypot"
    print "--------------"
    print "AMUN_X           : " + database['AMUN_X'].__str__()
    print "AMUN_AA          : " + database['AMUN_AA'].__str__()
    print " "
    print "SSH Honeypot"
    print "------------"
    print "KIPPO_CONN       : " + database['KIPPO_CONN'].__str__()
    print "KIPPO_LOGIN_FAIL : " + database['KIPPO_LOGIN_FAIL'].__str__()
    print "KIPPO_LOGIN_OK   : " + database['KIPPO_LOGIN_OK'].__str__()
    print "KIPPO_CMD        : " + database['KIPPO_CMD'].__str__()
    print "KIPPO_DL_START   : " + database['KIPPO_DL_START'].__str__()
    print "KIPPO_DL_FILE    : " + database['KIPPO_DL_FILE'].__str__()
    print "KIPPO_DL_STOP    : " + database['KIPPO_DL_STOP'].__str__()
    print "KIPPO_CONN_LOST  : " + database['KIPPO_CONN_LOST'].__str__()
    print " "
    print "Telnet Honeypot"
    print "---------------"
    print "TELNET_CONN       : " + database['TELNET_CONN'].__str__()
    print "TELNET_LOGIN_FAIL : " + database['TELNET_LOGIN_FAIL'].__str__()
    print "TELNET_LOGIN_OK   : " + database['TELNET_LOGIN_OK'].__str__()
    print "TELNET_CMD        : " + database['TELNET_CMD'].__str__()
    print "TELNET_CONN_LOST  : " + database['TELNET_CONN_LOST'].__str__()
    print " "
    print "Default Honeypot"
    print "----------------"
    print "HONEYTRAP_ALL    : " + database['HONEYTRAP_ALL'].__str__()
    print "HONEYTRAP_ATTACK : " + database['HONEYTRAP_ATTACK'].__str__()
    print "HONEYTRAP_ERROR  : " + database['HONEYTRAP_ERROR'].__str__()
    print " "
    print "Scanning"
    print "--------"
    print "TCP_PORTSCAN     : " + database['TCP_PORTSCAN'].__str__()
    print "TCP_SYNSCAN      : " + database['TCP_SYNSCAN'].__str__()
    print "UDP_SCAN         : " + database['UDP_SCAN'].__str__()
    print " "
    print "IDS Events"
    print "----------"
    print "NIDS_SU          : " + database['NIDS_SU'].__str__()
    print "NIDS_SH          : " + database['NIDS_SH'].__str__()   
    print " "
    print "Attacker Reconaissance"
    print "----------------------"
    print "GURU             : " + database['GURU'].__str__()
    print "NMAP             : " + database['NMAP'].__str__()
    print "TRACEROUTE       : " + database['TRACEROUTE'].__str__()
    print " "
    print "Attacker Fingerprinting"
    print "-----------------------"
    print "NMAP_WINDOWS     : " + database['NMAP_WINDOWS'].__str__()
    print "NMAP_LINUX       : " + database['NMAP_LINUX'].__str__()
    print "NMAP_FREEBSD     : " + database['NMAP_FREEBSD'].__str__()
    print "NMAP_OPENBSD     : " + database['NMAP_OPENBSD'].__str__()
    print "NMAP_CISCO       : " + database['NMAP_CISCO'].__str__()
    print " "
    print "Malware Analysis"
    print "----------------"
    print "CLAMAV           : " + database['CLAMAV'].__str__()
    print "FILE             : " + database['FILE'].__str__()
    print "SANDBOX          : " + database['SANDBOX'].__str__()
    print " "
    print "Twitter"
    print "-------"
    print "TWEET_API                  : " + database['TWEET_API'].__str__()
    print "TWEET_CORRELATED           : " + database['TWEET_CORRELATED'].__str__()
    print "TWEET_EXCEPTIONS           : " + database['TWEET_EXCEPTIONS'].__str__()
    print "TWEET_INTEREST             : " + database['TWEET_INTEREST'].__str__()
    print "TWEEPY_API_TOO_LONG        : " + database['TWEEPY_API_TOO_LONG'].__str__()
    print "TWEEPY_API_DAILY_LIMIT     : " + database['TWEEPY_API_DAILY_LIMIT'].__str__()
    print "TWEEPY_API_OAUTH_FAIL      : " + database['TWEEPY_API_OAUTH_FAIL'].__str__()
    print "TWEEPY_API_SEND_FAIL_PEER_RESET      : " + database['TWEEPY_API_SEND_FAIL_PEER_RESET'].__str__()
    print "TWEEPY_API_SEND_FAIL_NAME_RESOLUTION : " + database['TWEEPY_API_SEND_FAIL_NAME_RESOLUTION'].__str__()
    print "TWEEPY_API_INVALID_UNICODE : " + database['TWEEPY_API_INVALID_UNICODE'].__str__()
    print " "
    print "BRX"
    print "-------"
    print "BRX_LOGIN_OK      : " + database['BRX_LOGIN_OK'].__str__()
    print "BRX_LOGIN_FAIL    : " + database['BRX_LOGIN_FAIL'].__str__()
    print "BRX_EVENT_OK      : " + database['BRX_EVENT_OK'].__str__()
    print "BRX_EVENT_FAIL    : " + database['BRX_EVENT_FAIL'].__str__()
    print " "
    print "Team Cymru Whois caching"
    print "------------------------"
    print "CYMRU_WHOIS_CACHE_HIT  : " + database['CYMRU_WHOIS_CACHE_HIT'].__str__()
    print "CYMRU_WHOIS_CACHE_MISS : " + database['CYMRU_WHOIS_CACHE_MISS'].__str__()
    print " "
    print "Dnsmasq"
    print "-------"
    print "DNS_ALL           : " + database['DNS_ALL'].__str__()
    print "DNS_QUERY         : " + database['DNS_QUERY'].__str__()
    print "DNS_FORWARDED     : " + database['DNS_FORWARDED'].__str__()
    print "DNS_REPLY         : " + database['DNS_REPLY'].__str__()
    print "DNS_CACHED        : " + database['DNS_CACHED'].__str__()
    print "DNS_NXDOMAIN_IPV4 : " + database['DNS_NXDOMAIN_IPV4'].__str__()
    print "DNS_NXDOMAIN_IPV6 : " + database['DNS_NXDOMAIN_IPV6'].__str__()
    print " "
    print "Other"
    print "-----"
    print "REBOOT           : " + database['REBOOT'].__str__()
    print "ALL_ERRORS       : " + database['ALL_ERRORS'].__str__()
    print "ALL_WARNINGS     : " + database['ALL_WARNINGS'].__str__()
    print "MEMORY_HOG       : " + database['MEMORY_HOG'].__str__()
    print "CPU_HOG          : " + database['CPU_HOG'].__str__()
    print "PROCESS_RESTARTS : " + database['PROCESS_RESTARTS'].__str__()
    print " "
    print "TOTAL            : " + database['TOTAL'].__str__()
    print " "    
    nowLocal = time.gmtime(database['LAST_UPDATE_TIME'])
    #twitter_geoip.py:###makeMsg(0,"0","system,kojoney_viz started with pid=" + `pid` + " at localtime " + time.asctime(nowLocal))
    print "LAST_UPDATE_TIME : " + database['LAST_UPDATE_TIME'].__str__() + " -> " + time.asctime(nowLocal)
    print " "
        
if __name__ == "__main__" :
    
    printSnmpOIDs()
    printAttackerOIDs()   
    #printSnmpOIDs()
            