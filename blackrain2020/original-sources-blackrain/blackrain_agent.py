#!/usr/bin/python
import sys
import syslog
#import random
import shelve

#case "$1" in
#-g)     echo ".1.3.6.1.4.1.55555.1"  # you are enterprise 55555
#        echo "gauge"
#         echo "232323"
#         ;;
#         esac

PrivateOID = ".1.3.6.1.4.1"
MyRootOID  = ".55555"

# OIDs related to attacker IP characteristics
Oid2Shelf2 = {
'20.99'    : 'IP',	                # list of unique IPs attacking the honeynet as per netflow data
'20.1'     : 'NUM_IP',		        # number of unique IPs attacking honeynet
'20.2'     : 'NUM_SLASH_24',	        # number of unique /24 of IPs attacking honeynet
'20.3'     : 'NUM_CC',		        # number of unique countries of IPs attacking honeynet
'20.4'     : 'NUM_CITY',	        # number of unique cities of IPs attacking honeynet
'20.5'     : 'NUM_ASN',		        # number of unique ASN numbers of IPs attacking honeynet
'21.1'     : 'AMUN_FILES_BIN', 	        # number of unique binary files downloaded by Amun
'21.2'     : 'AMUN_FILES_HEX', 	        # number of unique hexdumps downloaded by Amun
'21.3'     : 'NEPENTHES_FILES', 	# number of unique binary files downloaded by Amun
'21.4'     : 'KIPPO_FILES', 		# number of unique binary files downloaded by Amun
'21.5'     : 'GLASTOPF_FILES_GET', 	# number of unique binary files downloaded by Amun
'21.6'     : 'GLASTOPF_FILES_POST', 	# number of unique binary files downloaded by Amun
'21.7'     : 'ANALYST_FILES_ALL', 	# number of all files  downloaded by Analyst
'21.8'     : 'ANALYST_FILES_EXE', 	# number of exe files  downloaded by Analyst
'21.9'     : 'ANALYST_FILES_PHP', 	# number of PHP files  downloaded by Analyst
'21.10'    : 'ANALYST_FILES_TXT', 	# number of text files downloaded by Analyst
'21.11'    : 'ANALYST_FILES_GIF', 	# number of gif files  downloaded by Analyst
'21.12'    : 'ANALYST_FILES_JPG', 	# number of jpg files  downloaded by Analyst
'21.13'    : 'ANALYST_FILES_PNG', 	# number of png files  downloaded by Analyst
'21.14'    : 'ANALYST_FILES_TGZ'  	# number of tgz files  downloaded by Analyst
}

#'20.2'     : 'TWEET_CORRELATED',
#'20.3'     : 'TWEET_EXCEPTIONS',
#'20.4'     : 'TWEET_INTEREST',

Oid2Shelf = {
'4.1'     : 'TWEET_API',
'4.2'     : 'TWEET_CORRELATED',
'4.3'     : 'TWEET_EXCEPTIONS',
'4.4'     : 'TWEET_INTEREST',
'2.1'     : 'ALL_ERRORS',
'2.2'     : 'ALL_WARNINGS',
'2.3'     : 'REBOOT',
'2.4'     : 'MEMORY_HOG',
'2.5'     : 'CPU_HOG',
'2.6'     : 'PROCESS_RESTARTS',
'3.1.1'   : 'AMUN_X',
'3.1.2'   : 'AMUN_AA',        
'3.2.1'   : 'WEB_SCAN',
'3.2.2'   : 'WEB_X_GET',        
'3.2.3'   : 'WEB_X_POST',       
'3.2.4'   : 'WEB_PRX',          
'3.2.5'   : 'WEB_OPEN',         
'3.2.6'   : 'WEB_WRITE',
'3.3.1'   : 'TCP_PORTSCAN',
'3.3.2'   : 'TCP_SYNSCAN',
'3.3.3'   : 'UDP_SCAN',       
'3.4.1'   : 'HONEYTRAP_ATTACK',       
'3.5.1'   : 'GURU',
'3.6.1'   : 'NMAP',
'3.6.2'   : 'TRACEROUTE',
'3.7.1.1' : 'NIDS_SU',
'3.7.2.1' : 'NIDS_SH',
'3.8.1'   : 'KIPPO_CONN',
'3.8.2'   : 'KIPPO_LOGIN_OK',
'3.8.3'   : 'KIPPO_LOGIN_FAIL',
'3.8.4'   : 'KIPPO_CMD',
'3.8.5'   : 'KIPPO_DL_START',
'3.8.6'   : 'KIPPO_DL_FILE',
'3.8.7'   : 'KIPPO_DL_STOP',
'3.8.8'   : 'KIPPO_CONN_LOST',
'3.9.1'   : 'NMAP_WINDOWS',
'3.9.2'   : 'NMAP_LINUX',
'3.9.3'   : 'NMAP_FREEBSD',
'3.9.4'   : 'NMAP_OPENBSD',
'3.9.5'   : 'NMAP_CISCO',       
'3.9.6'   : 'NMAP_UNIX',       
'3.10.1'  : 'SANDBOX',
'3.11.1'  : 'CLAMAV',
'3.12.1'  : 'FILE',
'3.13.1'  : 'DNS_ALL',
'3.13.2'  : 'DNS_QUERY',
'3.13.3'  : 'DNS_FORWARDED',
'3.13.4'  : 'DNS_CACHED',
'3.13.5'  : 'DNS_REPLY',
'3.13.6'  : 'DNS_NXDOMAIN_IPV4',
'3.13.7'  : 'DNS_NXDOMAIN_IPV6',
'3.14.1'  : 'TELNET_CONN',
'3.14.2'  : 'TELNET_LOGIN_OK',
'3.14.3'  : 'TELNET_LOGIN_FAIL',
'3.14.4'  : 'TELNET_CMD',
'3.14.5'  : 'TELNET_CONN_LOST',
'5.1'     : 'NETFLOW_IN',
'5.2'     : 'NETFLOW_OUT',
'5.6.1'   : 'NETFLOW_OTHER',
'5.6.2'   : 'NETFLOW_TROJAN',
'5.6.3'   : 'NETFLOW_SSH_2222',
'5.6.4'   : 'NETFLOW_SSH',
'5.6.5'   : 'NETFLOW_TELNET',
'5.6.6'   : 'NETFLOW_FTP_65XXX',
'5.6.7'   : 'NETFLOW_FTP_DATA',
'5.6.8'   : 'NETFLOW_FTP_CONTROL',
'5.6.9'   : 'NETFLOW_TFTP',
'5.6.10'  : 'NETFLOW_DNS',
'5.6.11'  : 'NETFLOW_FINGER',
'5.6.12'  : 'NETFLOW_HTTP_18080',
'5.6.13'  : 'NETFLOW_HTTP',
'5.6.14'  : 'NETFLOW_HTTPS',
'5.6.15'  : 'NETFLOW_HTTP_8080',
'5.6.16'  : 'NETFLOW_HTTP_3128',
'5.6.17'  : 'NETFLOW_SNMP',
'5.6.18'  : 'NETFLOW_SMTP',
'5.6.19'  : 'NETFLOW_IDENT',
'5.6.20'  : 'NETFLOW_SIP',
'5.6.21'  : 'NETFLOW_RDP',
'5.6.22'  : 'NETFLOW_POP3',
'5.6.23'  : 'NETFLOW_IRCD',
'5.6.24'  : 'NETFLOW_VNC',
'5.6.25'  : 'NETFLOW_PPTP',
'5.6.26'  : 'NETFLOW_445',
'5.6.27'  : 'NETFLOW_135',
'5.6.28'  : 'NETFLOW_137',
'5.6.29'  : 'NETFLOW_138',
'5.6.30'  : 'NETFLOW_139',
'5.6.31'  : 'NETFLOW_1433',
'5.6.32'  : 'NETFLOW_1434',
'5.6.33'  : 'NETFLOW_3306',
'5.6.34'  : 'NETFLOW_TELNET_10023',
'5.6.35'  : 'NETFLOW_SMTP_10025',
'5.6.36'  : 'NETFLOW_2967',
'5.6.37'  : 'NETFLOW_111',
'5.6.38'  : 'NETFLOW_5000',
'5.6.39'  : 'NETFLOW_4444',
'5.6.40'  : 'NETFLOW_4899',
'12.1'    : 'BRX_LOGIN_OK',
'12.2'    : 'BRX_LOGIN_FAIL',
'12.3'    : 'BRX_EVENT_OK',
'12.4'    : 'BRX_EVENT_FAIL',
'22.1'    : 'CYMRU_WHOIS_CACHE_HIT',
'22.2'    : 'CYMRU_WHOIS_CACHE_MISS'
}
          
def getOID(database,oid) :          
    global Oid2Shelf
    
    try :
        #syslog.syslog("Entered getOID(), looking for " + oid)
        
        oidRoot = PrivateOID + MyRootOID + "."
        #print "oidRoot is " + oidRoot
        oid2Find = oid.replace(oidRoot,"")	# strip of leading part of OID
        #print "oid2Find is " + oid2Find
    
        if Oid2Shelf.has_key(oid2Find) == True :
            value = database[Oid2Shelf[oid2Find]]
            return value
        else:
            return None    
            
    except Exception,e:
        syslog.syslog("getOID() : Exception : " + e.__str__())

# attacker IP stats
# !!! combine this with getOID into a single function
def getOID2(database,oid) :          
    global Oid2Shelf2
    
    try :
        #syslog.syslog("Entered getOID2(), looking for " + oid)
        
        oidRoot = PrivateOID + MyRootOID + "."
        #print "oidRoot is " + oidRoot
        oid2Find = oid.replace(oidRoot,"")	# strip of leadingpart of OID
        #print "oid2Find is " + oid2Find
    
        if Oid2Shelf2.has_key(oid2Find) == True :
            value = database[Oid2Shelf2[oid2Find]]
            return value
        else:
            return None    

    except Exception,e:
        syslog.syslog("getOID2() : Exception : " + e.__str__())


        
if __name__ == '__main__' :
    
    try :
    
        syslog.openlog("blackrain_agent",syslog.LOG_PID,syslog.LOG_LOCAL2)
        oid = sys.argv[1]			# full OID
        
        oidRoot = PrivateOID + MyRootOID + "."
        oid2find = oid.replace(oidRoot,"")	# strip off leading part of the full OID
        
        #msg = "oid2find = " + oid2find		# e.g. 20.1
        #syslog.syslog(msg)
        
        # look in first shelf file
        # ------------------------
        #value = None
        if Oid2Shelf.has_key(oid2find) == True :                    
            database = shelve.open('/home/var/log/snmp_shelf.dat')
            value = getOID(database,oid)
            database.close()
        
            if value == None :     
                syslog.syslog("Error : shelf1 : SNMP get-request for OID " + oid + " returned value " + value.__str__())
            else:
                print oid
                print "counter"
                #print "gauge"
                print value
                #syslog.syslog("shelf1 : SNMP get-request OK for OID " + oid + " returned value " + value.__str__())
        
        # look in second shelf file
        # -------------------------
        #value = None
        if Oid2Shelf2.has_key(oid2find) == True :                    
            database = shelve.open('/home/var/log/attacker_shelf.dat')
            value = getOID2(database,oid)
            database.close()
        
            if value == None :     
                syslog.syslog("Error : shelf2 : SNMP get-request for OID " + oid + " returned value " + value.__str__())
            else:
                print oid
                #print "counter"
                print "gauge"
                print value
                #syslog.syslog("shelf2 : SNMP get-request OK for OID " + oid + " returned value " + value.__str__())
        
    except Exception,e :
        syslog.syslog("main() : Exception : " + e.__str__())
        
               