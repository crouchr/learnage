#!/usr/bin/python

import time, os , syslog 
import re
#import kojoney_funcs
#import ipintellib
#import twitter_funcs
#import kojoney_correlate
import shelve

snmpoidsShelfFile = '/home/var/log/snmp_shelf.dat'

# need this so program can be monitored by monit
# make this a library function
def makePidFile(name):
    pid = os.getpid()
    
    pidFilename = "/var/run/rchpids/" + name + ".pid"
    fp=open(pidFilename,'w')
    print >> fp,pid
    fp.close()            
    #print "pid is " + `pid`
    return pid	# returns None if failed
    
# Update shelved object with SNMP stats in it                                   
# look for errors in /var/log/messages
def updateSnmpOIDsErrors(database,line):
  
    try :      

        # Don't look for our own update messages
        if line.find("kojoney_statd") != -1 and line.find("Incremented") != -1 :
            return

        if line.find("reboot") != -1 :
            database['REBOOT'] = int(database['REBOOT']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key REBOOT to " + database['REBOOT'].__str__())       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        

        # BRX events
        # ----------
        if line.find("Brapi.push_event_details() call OK") != -1 and line.find("kojoney_tweet") != -1 :
            database['BRX_EVENT_OK'] = int(database['BRX_EVENT_OK']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key BRX_EVENT_OK to " + "null")       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1

        if line.find("Brapi.push_event_details() call WARNING") != -1 and line.find("kojoney_tweet") != -1 :
            database['BRX_EVENT_FAIL'] = int(database['BRX_EVENT_FAIL']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1

        # TeamCymru WHOIS caching 
        # -----------------------
        if line.find("WHOIS_CACHE_HIT") != -1 and line.find("ipintellib.py") != -1 :
            database['CYMRU_WHOIS_CACHE_HIT'] = int(database['CYMRU_WHOIS_CACHE_HIT']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
            
        if line.find("WHOIS_CACHE_MISS") != -1 and line.find("ipintellib.py") != -1 :
            database['CYMRU_WHOIS_CACHE_MISS'] = int(database['CYMRU_WHOIS_CACHE_MISS']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1

        
        # ps-monitor events
        # -----------------
        if line.find("ps-monitor") != -1 and line.find("PROCESS_DIED") != -1 :
            database['PROCESS_RESTARTS'] = int(database['PROCESS_RESTARTS']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key PROCESS_RESTARTS to " + database['PROCESS_RESTARTS'].__str__())       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("ps-monitor") != -1 and line.find("CPU_HOG") != -1 :
            database['CPU_HOG'] = int(database['CPU_HOG']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key CPU_HOG to " + database['CPU_HOG'].__str__())       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("ps-monitor") != -1 and line.find("MEMORY_HOG") != -1 :
            database['MEMORY_HOG'] = int(database['MEMORY_HOG']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key MEMORY_HOG to " + database['MEMORY_HOG'].__str__())       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        # Twitter API
        # -----------
        if line.find("kojoney_tweet_engine") != -1 and line.find("TWITTER_API") != -1 :
            database['TWEET_API'] = int(database['TWEET_API']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key TWEET_API to " + database['TWEET_API'].__str__())       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("kojoney_tweet_engine") != -1 and line.find("DROP_CORRELATED_TWEET") != -1 :
            database['TWEET_CORRELATED'] = int(database['TWEET_CORRELATED']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key TWEET_CORRELATED to " + database['TWEET_CORRELATED'].__str__())       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("exception") != -1 and line.find("sendTweet()") != -1 :
            database['TWEET_EXCEPTIONS'] = int(database['TWEET_EXCEPTIONS']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key TWEET_EXCEPTIONS to " + database['TWEET_EXCEPTIONS'].__str__())       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1

        if line.find("kojoney_tweet_engine") != -1 and line.find("User is over daily status limit") != -1 :
            database['TWEEPY_API_DAILY_LIMIT'] = int(database['TWEEPY_API_DAILY_LIMIT']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1

        if line.find("kojoney_tweet_engine") != -1 and line.find("The text of your tweet is too long") != -1 :
            database['TWEEPY_API_TOO_LONG'] = int(database['TWEEPY_API_TOO_LONG']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("kojoney_tweet_engine") != -1 and line.find("Could not authenticate with OAuth") != -1 :
            database['TWEEPY_API_OAUTH_FAIL'] = int(database['TWEEPY_API_OAUTH_FAIL']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("kojoney_tweet_engine") != -1 and line.find("Invalid Unicode value in one") != -1 :
            database['TWEEPY_API_INVALID_UNICODE'] = int(database['TWEEPY_API_INVALID_UNICODE']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("kojoney_tweet_engine") != -1 and line.find("Connection reset by peer") != -1 :
            database['TWEEPY_API_SEND_FAIL_PEER_RESET'] = int(database['TWEEPY_API_SEND_FAIL_PEER_RESET']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("kojoney_tweet_engine") != -1 and line.find("name resolution") != -1 :
            database['TWEEPY_API_SEND_FAIL_NAME_RESOLUTION'] = int(database['TWEEPY_API_SEND_FAIL_NAME_RESOLUTION']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        # match on generic events
        # -----------------------
        if line.find("exception") != -1 or line.find("error") != -1 or line.find("Exception") != -1 or line.find("Error") != -1:
            database['ALL_ERRORS'] = int(database['ALL_ERRORS']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key ALL_ERRORS to " + database['ALL_ERRORS'].__str__())       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1

        if line.find("warning") != -1 or line.find("Warning") != -1 or line.find("WARNING") != -1 :
            database['ALL_WARNINGS'] = int(database['ALL_WARNINGS']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key ALL_WARNINGS to " + database['ALL_WARNINGS'].__str__())       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        # misc
        # ----
        # not really an error ...
        if line.find("tweetsOfInterest()") != -1 :
            database['TWEET_INTEREST'] = int(database['TWEET_INTEREST']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key TWEET_INTEREST to " + database['TWEET_INTEREST'].__str__())       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
                 
    except Exception,e:    
        syslog.syslog("kojoney_statd.py : updateSnmpOIDsErrors() : exception caught = " + `e` + " line=" + line)
                                       
                                       
def updateSnmpOIDsNetflow(database,line) :
  
    try :      

        #print "entered updateSnmpOIDsNetflow, line=" + line
        
        if line.find("dir=in") != -1 :
            database['NETFLOW_IN'] = int(database['NETFLOW_IN']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("dir=out") != -1 :
            database['NETFLOW_OUT'] = int(database['NETFLOW_OUT']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("pr=17 ") != -1 and line.find("dP=69 ") != -1 : 
            database['NETFLOW_TFTP'] = int(database['NETFLOW_TFTP']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        # http://www.chebucto.ns.ca/~rakerman/trojan-port-table.html
        # only on ports not otherwise used
        if line.find("dP=5554 ") != -1 or line.find("dP=2283 ") != -1 or line.find("dP=2535 ") != -1 or line.find("dP=2745 ") != -1 or line.find("dP=3127 ") != -1 or line.find("dP=7777 ") != -1 : 
            database['NETFLOW_TROJAN'] = int(database['NETFLOW_TROJAN']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("pr=6 ") != -1 and line.find("dP=23 ") != -1 : 
            database['NETFLOW_TELNET'] = int(database['NETFLOW_TELNET']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("pr=6 ") != -1 and line.find("dP=80 ") != -1 : 
            database['NETFLOW_HTTP'] = int(database['NETFLOW_HTTP']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("pr=6 ") != -1 and line.find("dP=18080 ") != -1 : 
            database['NETFLOW_HTTP_18080'] = int(database['NETFLOW_HTTP_18080']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("pr=6 ") != -1 and line.find("dP=8080 ") != -1 : 
            database['NETFLOW_HTTP_8080'] = int(database['NETFLOW_HTTP_8080']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("pr=6 ") != -1 and line.find("dP=3128 ") != -1 : 
            database['NETFLOW_HTTP_3128'] = int(database['NETFLOW_HTTP_3128']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("pr=6 ") != -1 and line.find("dP=6667 ") != -1 : 
            database['NETFLOW_IRCD'] = int(database['NETFLOW_IRCD']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("pr=6 ") != -1 and line.find("dP=5900 ") != -1 : 
            database['NETFLOW_VNC'] = int(database['NETFLOW_VNC']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("pr=6 ") != -1 and line.find("dP=1723 ") != -1 : 
            database['NETFLOW_PPTP'] = int(database['NETFLOW_PPTP']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("pr=6 ") != -1 and line.find("dP=443 ") != -1 : 
            database['NETFLOW_HTTPS'] = int(database['NETFLOW_HTTPS']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("pr=6 ") != -1 and line.find("dP=22 ") != -1 : 
            database['NETFLOW_SSH'] = int(database['NETFLOW_SSH']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("pr=6 ") != -1 and line.find("dP=2222 ") != -1 : 
            database['NETFLOW_SSH_2222'] = int(database['NETFLOW_SSH_2222']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("dP=445 ") != -1 : 
            database['NETFLOW_445'] = int(database['NETFLOW_445']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("dP=135 ") != -1 : 
            database['NETFLOW_135'] = int(database['NETFLOW_135']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("dP=137 ") != -1 : 
            database['NETFLOW_137'] = int(database['NETFLOW_137']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
             
        if line.find("dP=138 ") != -1 : 
            database['NETFLOW_138'] = int(database['NETFLOW_138']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("dP=139 ") != -1 : 
            database['NETFLOW_139'] = int(database['NETFLOW_139']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("dP=161 ") != -1 : 
            database['NETFLOW_SNMP'] = int(database['NETFLOW_SNMP']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("dP=5060 ") != -1 : 
            database['NETFLOW_SIP'] = int(database['NETFLOW_SIP']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("dP=53 ") != -1 : 
            database['NETFLOW_DNS'] = int(database['NETFLOW_DNS']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("dP=3389 ") != -1 : 
            database['NETFLOW_RDP'] = int(database['NETFLOW_RDP']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("dP=113 ") != -1 : 
            database['NETFLOW_IDENT'] = int(database['NETFLOW_IDENT']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("dP=79 ") != -1 : 
            database['NETFLOW_FINGER'] = int(database['NETFLOW_FINGER']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
      
        if line.find("dP=110 ") != -1 : 
            database['NETFLOW_POP3'] = int(database['NETFLOW_POP3']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("dP=25 ") != -1 : 
            database['NETFLOW_SMTP'] = int(database['NETFLOW_SMTP']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        # Traffic to faketelnetd
        if line.find("dP=10025 ") != -1 : 
            database['NETFLOW_SMTP_10025'] = int(database['NETFLOW_SMTP_10025']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        # Traffic to spamhole
        if line.find("dP=10023 ") != -1 : 
            database['NETFLOW_TELNET_10023'] = int(database['NETFLOW_TELNET_10023']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
      
        if line.find("dP=21 ") != -1 : 
            database['NETFLOW_FTP_CONTROL'] = int(database['NETFLOW_FTP_CONTROL']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
      
        if line.find("dP=20 ") != -1 : 
            database['NETFLOW_FTP_DATA'] = int(database['NETFLOW_FTP_DATA']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
      
        if line.find("dP=62001 ") != -1 or line.find("dP=62002 ") != -1 or line.find("dP=62003 ") != -1 : 
            database['NETFLOW_FTP_65XXX'] = int(database['NETFLOW_FTP_65XXX']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
      
        return                 
    
    except Exception,e:    
        syslog.syslog("kojoney_statd.py : updateSnmpOIDsNetflow() : exception caught = " + `e` + " line=" + line)

def updateSnmpOIDsKippo(database,line) :
  
    try :      

        #print "entered updateSnmpOIDsKippo, line=" + line
        
        # need to add to shelf
        if line.find("Remote SSH version") != -1 :
            database['KIPPO_CONN'] = int(database['KIPPO_CONN']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key KIPPO_CONN to " + "null")       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1

        if line.find("login attempt") != -1 and line.find("succeeded") != -1 :
            database['KIPPO_LOGIN_OK'] = int(database['KIPPO_LOGIN_OK']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key KIPPO_LOGIN_OK to " + database['KIPPO_LOGIN_OK'].__str__())       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("login attempt") != -1 and line.find("failed") != -1 :
            database['KIPPO_LOGIN_FAIL'] = int(database['KIPPO_LOGIN_FAIL']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key KIPPO_LOGIN_FAIL to " + database['KIPPO_LOGIN_FAIL'].__str__())       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("Command found:") != -1 :
            database['KIPPO_CMD'] = int(database['KIPPO_CMD']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key KIPPO_CMD to " + database['KIPPO_CMD'].__str__())       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
            
        # need to add to shelf
        if line.find("Starting factory <HTTPProgressDownloader:") != -1 :
            database['KIPPO_DL_START'] = int(database['KIPPO_DL_START']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key KIPPO_DL_START to " + "null")       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        # need to add to shelf - actually downloaded a file
        if line.find("Updating realfile to ") != -1 :
            database['KIPPO_DL_FILE'] = int(database['KIPPO_DL_FILE']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key KIPPO_DL_FILE to " + "null")       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        # need to add to shelf
        if line.find("Stopping factory <HTTPProgressDownloader:") != -1 :
            database['KIPPO_DL_STOP'] = int(database['KIPPO_DL_STOP']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key KIPPO_DL_STOP to " + "null")       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        # need to add to shelf
        if line.find("connection lost") != -1 :
            database['KIPPO_CONN_LOST'] = int(database['KIPPO_CONN_LOST']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key KIPPO_CONN_LOST to " + "null")       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1

        return                  
    
    except Exception,e:    
        syslog.syslog("kojoney_statd.py : updateSnmpOIDsKippo() : exception caught = " + `e` + " line=" + line)

def updateSnmpOIDsTelnet(database,line) :
  
    try :      

        #print "entered updateSnmpOIDsTelnet, line=" + line
        
        # need to add to shelf
        if line.find("Incoming connection from") != -1 :
            database['TELNET_CONN'] = int(database['TELNET_CONN']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key TELNET_CONN to " + "null")       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1

        if line.find("INFO: Successful login from") != -1 :
            database['TELNET_LOGIN_OK'] = int(database['TELNET_LOGIN_OK']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key TELNET_LOGIN_OK to " + "null")       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("INFO: Failed login from") != -1 :
            database['TELNET_LOGIN_FAIL'] = int(database['TELNET_LOGIN_FAIL']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key TELNET_LOGIN_FAIL to " + "null")       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("entered command:") != -1 :
            database['TELNET_CMD'] = int(database['TELNET_CMD']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key TELNET_CMD to " + "null")       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
            
        # need to add to shelf
        if line.find("Ending session") != -1 :
            database['TELNET_CONN_LOST'] = int(database['TELNET_CONN_LOST']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key TELNET_CONN_LOST to " + "null")       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1

        return                  
    
    except Exception,e:    
        syslog.syslog("kojoney_statd.py : updateSnmpOIDsTelnet() : exception caught = " + `e` + " line=" + line)
                                       
def updateSnmpOIDsDns(database,line) :
  
    try :      

        #print "entered updateSnmpOIDsDns, line=" + line
        
        # need to add to shelf
        if line.find("dnsmasq") != -1 :
            database['DNS_ALL'] = int(database['DNS_ALL']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key DNS_ALL to " + "null")       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1

        if line.find("query") != -1 :
            database['DNS_QUERY'] = int(database['DNS_QUERY']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key DNS_QUERY to " + "null")       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("forwarded") != -1 :
            database['DNS_FORWARDED'] = int(database['DNS_FORWARDED']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key DNS_FORWARDED to " + "null")       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("reply") != -1 :
            database['DNS_REPLY'] = int(database['DNS_REPLY']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key DNS_REPLY to " + "null")       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
            
        # need to add to shelf
        if line.find("cached") != -1 :
            database['DNS_CACHED'] = int(database['DNS_CACHED']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key DNS_CACHED to " + "null")       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1

        # need to add to shelf
        if line.find("NXDOMAIN-IPv4") != -1 :
            #pass
            database['DNS_NXDOMAIN_IPV4'] = int(database['DNS_NXDOMAIN_IPV4']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key DNS_NXDOMAIN_IPV4 to " + "null")       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("NXDOMAIN-IPv6") != -1 :
            #pass
            database['DNS_NXDOMAIN_IPV6'] = int(database['DNS_NXDOMAIN_IPV6']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key DNS_NXDOMAIN_IPV6 to " + "null")       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1

        return                  
    
    except Exception,e:    
        syslog.syslog("kojoney_statd.py : updateSnmpOIDsDns() : exception caught = " + `e` + " line=" + line)
                                       
                            
# Update shelved object with SNMP stats in it                                   
# Look for events in the tweets queue
def updateSnmpOIDs(database,line):
  
    try :      

        # Don't look for our own messages
        #if line.find("kojoney_statd") != -1 and line.find("Incremented") != -1 :
        #    return
            
        # update attacker OS (as determined by nmap active scan)
        if line.find("NMAP") != -1 and line.find("Windows") != -1 :
            database['NMAP_WINDOWS'] = int(database['NMAP_WINDOWS']) + 1
        
        if line.find("NMAP") != -1 and line.find("Linux") != -1 :
            database['NMAP_LINUX'] = int(database['NMAP_LINUX']) + 1
        
        if line.find("NMAP") != -1 and line.find("FreeBSD") != -1 :
            database['NMAP_FREEBSD'] = int(database['NMAP_FREEBSD']) + 1
        
        if line.find("NMAP") != -1 and line.find("OpenBSD") != -1 :
            database['NMAP_OPENBSD'] = int(database['NMAP_OPENBSD']) + 1
        
        if line.find("NMAP") != -1 and line.find("IOS") != -1 :
            database['NMAP_CISCO'] = int(database['NMAP_CISCO']) + 1
        
        if line.find("NMAP") != -1 and line.find("Unix") != -1 :
            database['NMAP_UNIX'] = int(database['NMAP_UNIX']) + 1
        
        if line.find("WEB_SCN") != -1 :
            database['WEB_SCAN'] = int(database['WEB_SCAN']) + 1
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1   
            #syslog.syslog("Incremented snmpoids shelf object key WEB_SCAN to " + database['WEB_SCAN'].__str__())        
        
        if line.find("WEB_X,GET") != -1 :
            database['WEB_X_GET'] = int(database['WEB_X_GET']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key WEB_X_GET to " + database['WEB_X_GET'].__str__())        
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
    
        if line.find("WEB_X,POST") != -1 :
            database['WEB_X_POST'] = int(database['WEB_X_POST']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key WEB_X_POST to " + database['WEB_X_POST'].__str__())        
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
    
        if line.find("WEB_PRX") != -1 :
            database['WEB_PRX'] = int(database['WEB_PRX']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key WEB_PRX to " + database['WEB_PRX'].__str__())         
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
    
        if line.find("WEB_OPEN") != -1 :
            database['WEB_OPEN'] = int(database['WEB_OPEN']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key WEB_OPEN to " + database['WEB_OPEN'].__str__())        
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
    
        if line.find("AMUN_X") != -1 :
            database['AMUN_X'] = int(database['AMUN_X']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key AMUN_X to " + database['AMUN_X'].__str__())        
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
    
        if line.find("AMUN_AA") != -1 :
            database['AMUN_AA'] = int(database['AMUN_AA']) + 1
            #Bsyslog.syslog("Incremented snmpoids shelf object key AMUN_AA to " + database['AMUN_AA'].__str__())        
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
    
        if line.find("HTRAP") != -1 :
            database['HONEYTRAP_ATTACK'] = int(database['HONEYTRAP_ATTACK']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key HONEYTRAP_ATTACK to " + database['HONEYTRAP_ATTACK'].__str__())        
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
    
        #if line.find("KIPPO_INT") != -1 :
        #    database['KIPPO'] = int(database['KIPPO']) + 1
        #    syslog.syslog("Incremented snmpoids shelf object key KIPPO to " + database['KIPPO'].__str__())        
        #    database['LAST_UPDATE_TIME'] = time.time()
        #    database['TOTAL']            = int(database['TOTAL']) + 1
    
        if line.find("NIDS_SU") != -1 :
            database['NIDS_SU'] = int(database['NIDS_SU']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key NIDS_SU to " + database['NIDS_SU'].__str__())      
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
    
        if line.find("SNORT_NIDS") != -1 :
            database['NIDS_SH'] = int(database['NIDS_SH']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key NIDS_SH to " + database['NIDS_SH'].__str__())        
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
       
        if line.find("GURU") != -1 :
            database['GURU'] = int(database['GURU']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key GURU to " + database['GURU'].__str__())    
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
           
        if line.find("NMAP") != -1 :
            database['NMAP'] = int(database['NMAP']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key NMAP to " + database['NMAP'].__str__())        
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
       
        if line.find("TRACEROUTE") != -1 :
            database['TRACEROUTE'] = int(database['TRACEROUTE']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key TRACEROUTE to " + database['TRACEROUTE'].__str__())        
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
       
        if line.find("TCP portscan detected") != -1 :
            database['TCP_PORTSCAN'] = int(database['TCP_PORTSCAN']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key TCP_PORTSCAN  to " + database['TCP_PORTSCAN'].__str__())        
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
        
        if line.find("TCP SYN scan detected") != -1 :
            database['TCP_SYNSCAN'] = int(database['TCP_SYNSCAN']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key TCP_SYNSCAN  to " + database['TCP_SYNSCAN'].__str__())        
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
           
        if line.find("UDP scan/flood detected") != -1 :
            database['UDP_SCAN'] = int(database['UDP_SCAN']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key UDP_SCAN to " + database['UDP_SCAN'].__str__())       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
    
        if line.find("AV ClamAV->") != -1 :
            database['CLAMAV'] = int(database['CLAMAV']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key CLAMAV to " + database['CLAMAV'].__str__())      
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
       
        if line.find("FILE->") != -1 :
            database['FILE'] = int(database['FILE']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key FILE to " + database['FILE'].__str__())       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
       
        if line.find("SANDBOX->") != -1 :
            database['SANDBOX'] = int(database['SANDBOX']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key SANDBOX to " + database['SANDBOX'].__str__())        
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
           
        if line.find("WEB_WRITE") != -1 :
            database['WEB_WRITE'] = int(database['WEB_WRITE']) + 1
            #syslog.syslog("Incremented snmpoids shelf object key WEB_WRITE to " + database['WEB_WRITE'].__str__())       
            database['LAST_UPDATE_TIME'] = time.time()
            database['TOTAL']            = int(database['TOTAL']) + 1
                 
    except Exception,e:    
        syslog.syslog("kojoney_statd.py : updateSnmpOIDs() : exception caught = " + `e` + " line=" + line)
                                       
                                   
# -------------------------------------------------------
        
# Start of code        
syslog.openlog("kojoney_statd",syslog.LOG_PID,syslog.LOG_LOCAL2)         # Set syslog program name         
       
# Make pidfile so we can be monitored by monit        
pid =  makePidFile("kojoney_statd")
if pid == None:
    syslog.syslog("Failed to create pidfile for pid " + `pid`)
    sys.exit(0)
else:
    syslog.syslog("kojoney_statd.py started with pid " + `pid`)
    
#snmpoidsShelfFile = '/home/var/log/snmp_shelf.dat'
database = shelve.open(snmpoidsShelfFile)
if len(database) == 0 :		# contains no entries
    # .5.1
    database['NETFLOW_IN']          = 0	
    
    # .5.2
    database['NETFLOW_OUT']         = 0	
    
    # .5.3	
    database['NETFLOW_IN_BYTES']    = 0
    database['NETFLOW_IN_PKTS']     = 0	
    database['NETFLOW_OUT_BYTES']   = 0
    database['NETFLOW_OUT_PKTS']    = 0	
    database['NETFLOW_PORT0_IN_BYTES']    = 0	# port 0 in netflow
    database['NETFLOW_PORT0_IN_PKTS']     = 0	
    database['NETFLOW_PORT0_OUT_BYTES']   = 0
    database['NETFLOW_PORT0_OUT_PKTS']    = 0	
    
    # .5.4 - IP protocol
    database['NETFLOW_P_OTHER']     = 0		# none of the below
    database['NETFLOW_P_TCP']       = 0	
    database['NETFLOW_P_UDP']       = 0	
    database['NETFLOW_P_SCTP']      = 0	
    database['NETFLOW_P_ICMP']      = 0	
    database['NETFLOW_P_P41']       = 0		# IPv6 in IPv4	
    
    # .5.5
    database['NETFLOW_ICMP_OTHER']         = 0	# None of the below	
    database['NETFLOW_ICMP_ECHO_REQ']      = 0	
    database['NETFLOW_ICMP_ECHO_REP']      = 0	
    database['NETFLOW_ICMP_TSTAMP_REQ']    = 0	
    database['NETFLOW_ICMP_TSTAMP_REP']    = 0	
    database['NETFLOW_ICMP_NETMASK_REQ']   = 0	
    database['NETFLOW_ICMP_NETMASK_REP']   = 0	
    database['NETFLOW_ICMP_HOST_UNREACH']  = 0	
    database['NETFLOW_ICMP_NET_UNREACH']   = 0	
    database['NETFLOW_ICMP_PORT_UNREACH']  = 0	
    database['NETFLOW_ICMP_ADMIN_UNREACH'] = 0	
    database['NETFLOW_ICMP_OTHER_UNREACH'] = 0	
    
    # .5.6 - applications
    database['NETFLOW_OTHER']        = 0		# .1	
    database['NETFLOW_TROJAN']       = 0		# .2 Well-known trojan/backdoor ports e.g. 7777	
    database['NETFLOW_SSH_2222']     = 0	        # .3
    database['NETFLOW_SSH']          = 0		# .4 port 22	
    database['NETFLOW_TELNET']       = 0	        # .5
    database['NETFLOW_FTP_65XXX']    = 0		# .6  port forwarded FTP inbound fro Amun	 
    database['NETFLOW_FTP_DATA']     = 0		# .7 port 20	
    database['NETFLOW_FTP_CONTROL']  = 0	        # .8 port 21
    database['NETFLOW_TFTP']         = 0	        # .9
    database['NETFLOW_DNS']          = 0	        # .10
    database['NETFLOW_FINGER']       = 0		# .11 port 79
    database['NETFLOW_HTTP_18080']   = 0	        # .12 port 80
    database['NETFLOW_HTTP']         = 0	        # .13
    database['NETFLOW_HTTPS']        = 0	        # .14
    database['NETFLOW_HTTP_8080']    = 0	        # .15
    database['NETFLOW_HTTP_3128']    = 0		# .16 squid proxy well-known proxy	
    database['NETFLOW_SNMP']         = 0	        # .17 
    database['NETFLOW_SMTP']         = 0	        # .18
    database['NETFLOW_IDENT']        = 0		# .19 port 113
    database['NETFLOW_SIP']          = 0	        # .20
    database['NETFLOW_RDP']          = 0		# .21 port 3389
    database['NETFLOW_POP3']         = 0	        # .22
    database['NETFLOW_IRCD']         = 0                # .23	
    database['NETFLOW_VNC']          = 0		# .24 port 5900 and above	
    database['NETFLOW_PPTP']         = 0		# .25 port 1723	
    database['NETFLOW_445']          = 0	        # .26
    database['NETFLOW_135']          = 0	        # .27
    database['NETFLOW_137']          = 0	        # .28
    database['NETFLOW_138']          = 0	        # .29
    database['NETFLOW_139']          = 0	        # .30

    database['NETFLOW_1433']         = 0	# .31 ms-sql-server
    database['NETFLOW_1434']         = 0	# .32 ms-sql-monitor
    database['NETFLOW_3306']         = 0	# .33
    database['NETFLOW_TELNET_10023'] = 0	# .34 faketelnetd
    database['NETFLOW_SMTP_10025']   = 0	# .35 spamhole
    database['NETFLOW_2967']         = 0	# .36
    database['NETFLOW_111']          = 0	# .37
    database['NETFLOW_5000']         = 0	# .38 upnp
    database['NETFLOW_4444']         = 0	# .39 upnp
    database['NETFLOW_4899']         = 0	# .40 radmin
    
    database['NETFLOW_LOW_NUM']        = 0	# .70	i.e. 1 - 19 
    database['NETFLOW_HIGH_NUM_10000'] = 0	# .71	i.e. >= port 10000
    database['NETFLOW_HIGH_NUM_20000'] = 0	# .72	i.e. >= port 20000
    database['NETFLOW_HIGH_NUM_30000'] = 0	# .73	i.e. >= port 30000
    database['NETFLOW_HIGH_NUM_40000'] = 0	# .74	i.e. >= port 40000
    database['NETFLOW_HIGH_NUM_50000'] = 0	# .75	i.e. >= port 50000
    database['NETFLOW_HIGH_NUM_60000'] = 0	# .76	i.e. >= port 60000
    
    
    # Regular IPTABLES : .6.x
    # .6.1.1
    database['IPTABLES_ACCEPT']     = 0	
    # .6.1.2
    database['IPTABLES_DROP']       = 0	
    
    # FWSNORT : .7.x
    # .7.1.1
    database['IPTABLES_FWSNORT_ACCEPT'] = 0	# IDS mode, i.e. just logging	
    # .7.1.2
    database['IPTABLES_FWSNORT_DROP']   = 0	# IPS mode (silent discard packet)
    # .7.1.3
    database['IPTABLES_FWSNORT_REJECT'] = 0	# IPS mode (TCP reset/ICMP unreachable)
    
    # Tools : .8.x - identify from IDS events
    # .8.1
    database['TOOL_OTHER']       = 0		# any not included below	
    database['TOOL_NMAP']        = 0		# 	
    database['TOOL_PING']        = 0		# 	
    database['TOOL_TRACEROUTE']  = 0		# 	
    database['TOOL_MORPHEUS']    = 0		# 	
    database['TOOL_NIKTO']       = 0		# 	
    database['TOOL_NESSUS']      = 0		# 	
    database['TOOL_SIPVICIOUS']  = 0		# 	
    database['TOOL_CYBERKIT']    = 0		# 	
    database['TOOL_XPROBE']      = 0		# 	
    database['TOOL_ZMEU']        = 0		# 	
    database['TOOL_BOT']         = 0		# e.g. NIDS_SU 2011286 Bot search RFI scan	
    
    # Networks : .9.x
    # Networks that generally attack/probe the honeynet
    database['NET_OTHER']        = 0		# any not included below 	
    database['NET_GOOGLE']       = 0		# 	
    database['NET_RBN']          = 0		# 	
    database['NET_TOR']          = 0		# 	
    database['NET_SUSP']         = 0		# Suspicious network	
    database['NET_BADACTOR']     = 0		# Known bad actor network	
    
    # Service Networks : .10.x
    # Networks that the Honeypot uses
    database['SVC_NET_OTHER']        = 0	# any not included below 	
    database['SVC_NET_BRX']	     = 0	#  	
    database['SVC_NET_TWITTER']      = 0	#  	
    database['SVC_NET_BITLY']        = 0	#  	
    database['SVC_NET_ANUBIS']       = 0	# 	
    database['SVC_NET_TEAM_CYMRU']   = 0	# WHOIS and Malware Index	
    database['SVC_NET_WHOIS']        = 0	# 	
    database['SVC_NET_EMERGING_THREATS']  = 0	# IDS updates 	
    database['SVC_NET_SLACKWARE_UPDATES'] = 0	# 	

    # Common Networks : .11.x
    database['NET_MICROSOFT']    = 0	 	
  
    # BRX API: .12.x
    database['BRX_LOGIN_OK']       = 0		# login to brx was OK	 	
    database['BRX_LOGIN_FAIL']     = 0		# login to brx failed	 	
    database['BRX_EVENT_OK']       = 0		# an action via the API was successful	 	
    database['BRX_EVENT_FAIL']     = 0		# an action via the API failed	 	
    
    # email: .13.x
    database['EMAIL_OK']       = 0		# an action requiring email was successful	 	
    database['EMAIL_FAIL']     = 0		# an action requiring email failed	 	
  
    # bitly : .14.x
    database['BITLY_API_OK']   = 0		# an action requiring bit.ly was successful	 	
    database['BITLY_API_FAIL'] = 0		# an action requiring bitly failed	 	
  
    # Network connectivity watchdog : .15.x
    database['NETWATCH_LAN_OK']   = 0		# network connectivty OK according to netwatchd	 	
    database['NETWATCH_LAN_FAIL'] = 0		# network connectivity failed according to netwatchd	 	
    database['NETWATCH_WAN_OK']   = 0		# network connectivty OK according to netwatchd	 	
    database['NETWATCH_WAN_FAIL'] = 0		# network connectivity failed according to netwatchd	 	
  
    # Monitored Networks : .16.x
    # Your own networks
    database['NET_MY_OTHER']      = 0		# any not included below 	
    database['NET_MY_1']          = 0		# e.g. Arcor and backbone	
    database['NET_MY_2']          = 0		# e.g. VF UK	
    database['NET_MY_3']          = 0		# 	
    database['NET_MY_4']          = 0		# 	
    database['NET_MY_5']          = 0		# 	
    database['NET_MY_6']          = 0		# 	
    database['NET_MY_7']          = 0		# 	
    database['NET_MY_8']          = 0		# 	
    database['NET_MY_9']          = 0		# 	
    database['NET_MY_10']         = 0		# 	
    database['NET_MY_11']         = 0		# 	
    database['NET_MY_12']         = 0		# 	
    database['NET_MY_13']         = 0		# 	
    database['NET_MY_14']         = 0		# 	
    database['NET_MY_15']         = 0		# 	
    database['NET_MY_16']         = 0		# 	
    database['NET_MY_17']         = 0		# 	
    database['NET_MY_18']         = 0		# 	
    database['NET_MY_19']         = 0		# 	
    database['NET_MY_20']         = 0		# 	
    
    # Misc : .17.x
    # Events that do not seem to fit anywhere else
    database['NMAP_TRIVIAL_JOKE'] = 0		#  	
    
    # TeamCymru Whois : .18.x
    database['CYMRU_WHOIS_CACHE_HIT']         = 0
    database['CYMRU_WHOIS_CACHE_MISS']        = 0

    # Passer : .19.x
    database['PASSER_BACKDOOR']               = 0
    
    # .3.2.x
    database['WEB_SCAN']         = 0
    database['WEB_X_GET']        = 0
    database['WEB_X_POST']       = 0
    database['WEB_PRX']          = 0
    database['WEB_OPEN']         = 0
    database['WEB_WRITE']        = 0
    database['WEB_SQLI']         = 0
    database['WEB_XSS']          = 0
    
    # .3.1.x
    database['AMUN_X']           = 0
    database['AMUN_AA']          = 0
    
    # .3.4.x
    database['HONEYTRAP_ALL']    = 0
    database['HONEYTRAP_ATTACK'] = 0
    database['HONEYTRAP_ERROR']  = 0
    
    # .3.8.x	SSHd and Telnetd
    database['KIPPO_CONN']       = 0
    database['KIPPO_LOGIN_FAIL'] = 0
    database['KIPPO_LOGIN_OK']   = 0
    database['KIPPO_CMD']        = 0
    database['KIPPO_DL_START']   = 0
    database['KIPPO_DL_FILE']    = 0
    database['KIPPO_DL_STOP']    = 0
    database['KIPPO_CONN_LOST']  = 0
    
    database['TELNET_CONN']       = 0
    database['TELNET_LOGIN_FAIL'] = 0
    database['TELNET_LOGIN_OK']   = 0
    database['TELNET_CMD']        = 0
    database['TELNET_CONN_LOST']  = 0
    
    # .3.7.x
    database['NIDS_SU']          = 0
    database['NIDS_SU_P1']       = 0	# Priority 1
    database['NIDS_SU_P2']       = 0	# Priority 2
    database['NIDS_SU_P3']       = 0    # Priority 3
    
    database['NIDS_SH']          = 0
    database['NIDS_SH_P1']       = 0
    database['NIDS_SH_P2']       = 0
    database['NIDS_SH_P3']       = 0
    
    database['GEO_OTHER']        = 0
    database['GEO_CN']           = 0
    database['GEO_HK']           = 0
    database['GEO_RU']           = 0
    database['GEO_RO']           = 0
    database['GEO_KR']           = 0
    database['GEO_ID']           = 0
    database['GEO_CO']           = 0
    database['GEO_VN']           = 0
    database['GEO_BR']           = 0
    database['GEO_IN']           = 0
    database['GEO_US']           = 0
    database['GEO_CA']           = 0
    database['GEO_GB']           = 0
    database['GEO_FR']           = 0
    database['GEO_DE']           = 0
    database['GEO_ES']           = 0
    
    database['REG_ARIN']         = 0
    database['REG_APNIC']        = 0
    database['REG_RIPENCC']      = 0
    database['REG_AFNIC']        = 0
    database['REG_LACNIC']       = 0
    
    # .3.5.x
    database['GURU']             = 0
    
    # .3.6.x
    database['NMAP']             = 0
    database['TRACEROUTE']       = 0
    
    # .3.3.x
    database['TCP_PORTSCAN']     = 0
    database['TCP_SYNSCAN']      = 0
    database['UDP_SCAN']         = 0
    
    # .3.10.x Sandbox
    # ---------------
    database['SANDBOX']          = 0 
    database['SANDBOX_NET']      = 0 
    database['SANDBOX_DNS']      = 0 
    database['SANDBOX_TCP']      = 0 
    database['SANDBOX_IRC']      = 0 
    
    # .3.11.x
    # -----------
    database['CLAMAV']           = 0
    
    # .3.12.x UNIX File command
    # ----------------------
    database['FILE']             = 0
    
    # .3.13.x DNS command
    # -------------------
    database['DNS_ALL']           = 0
    database['DNS_QUERY']         = 0
    database['DNS_FORWARDED']     = 0
    database['DNS_CACHED']        = 0
    database['DNS_REPLY']         = 0
    database['DNS_NXDOMAIN_IPV4'] = 0
    database['DNS_NXDOMAIN_IPV6'] = 0
    
    # .3.14.x Spamhole
    # ----------------
    database['SPAMHOLE_CONN']            = 0
    database['SPAMHOLE_NEW_SPAMMER']     = 0
    database['SPAMHOLE_TO_YE_HOLE']      = 0
    database['SPAMHOLE_MAIL_RX']         = 0
    database['SPAMHOLE_MAIL_RELAYED_OK'] = 0
    database['SPAMHOLE_MAIL_FAIL']       = 0
    
    # to be allocated
    # ---------------
    database['RBN_HOST']         = 0 
    database['DSHIELD_HOST']     = 0 
    database['HOSTILE_HOST']     = 0 
    database['BOTNET_CC_HOST']   = 0 
    
    database['NO_DNS']           = 0 
    database['WHOIS_FAILED']     = 0 
                        
    # .9 : OS of attackers - do not increment TOTAL
    database['NMAP_WINDOWS']     = 0
    database['NMAP_LINUX']       = 0
    database['NMAP_FREEBSD']     = 0
    database['NMAP_OPENBSD']     = 0
    database['NMAP_CISCO']       = 0
    database['NMAP_UNIX']        = 0   
    database['NMAP_SUNOS']       = 0   # not implemented. SunOS or Solaris
    database['NMAP_MOBILE']      = 0   # not implemented. e.g. Symbian
    database['NMAP_OTHER']       = 0   # not implemented
            
    # monitoring - /var/log/messages
    # .2 : general errors
    database['ALL_ERRORS']       = 0	# exceptions and errors
    database['ALL_WARNINGS']     = 0	# warnings
    database['REBOOT']           = 0
    database['MEMORY_HOG']       = 0	# a single process is using excessive memory - ps-monitor.py
    database['CPU_HOG']          = 0	# a single process is using excessive CPU - ps-monitor.py
    database['PROCESS_RESTARTS'] = 0	# process was restarted by ps-monitor
    
    #.4 Twitter API
    database['TWEET_API']        = 0	# Tweet was submitted into Twitter API
    database['TWEET_CORRELATED'] = 0	# Tweet was submitted into Twitter API
    database['TWEET_EXCEPTIONS'] = 0	# specifically Twitter-related exceptions
    database['TWEET_INTEREST']   = 0	# tweetsOfInterest            
    
    database['TWEEPY_API_TOO_LONG']    = 0			# "The text of your tweet is too long"            
    database['TWEEPY_API_DAILY_LIMIT'] = 0			# "User is over daily status update limit"            
    database['TWEEPY_API_OAUTH_FAIL']  = 0	   		# "Could not authenticate with OAuth"            
    database['TWEEPY_API_SEND_FAIL_PEER_RESET']      = 0	# "Failed to send request" , "Connection reset by peer"            
    database['TWEEPY_API_SEND_FAIL_NAME_RESOLUTION'] = 0	# "Failed to send request" , "Temporary failure in name resolution"            
    database['TWEEPY_API_INVALID_UNICODE'] = 0			# "Invalid Unicode value in one or more parameters"            
    
    # meta data
    database['LAST_UPDATE_TIME'] = 0
    database['TOTAL']            = 0
    
    database.close()
            
    syslog.syslog("No snmpoids shelf file found, so created an empty one in " + snmpoidsShelfFile)
else:
    syslog.syslog("snmpoids shelf file already exists, so will use it, filename=" + snmpoidsShelfFile)
    
    
                
# files to monitor
filename = '/home/var/log/tweet_queue.log' 			# real file
file     = open(filename,'r')

syslogFilename = '/var/log/messages'
syslogFile     = open(syslogFilename,'r')

netflowFilename = '/home/var/log/netflow.syslog'
netflowFile     = open(netflowFilename,'r')

kippoFilename = '/home/var/log/kippo.log'
kippoFile     = open(kippoFilename,'r')

dnsFilename = '/home/var/log/dnsmasq.syslog'
dnsFile     = open(dnsFilename,'r')

telnetFilename = '/home/var/log/faketelnetd.log'
telnetFile     = open(telnetFilename,'r')
            
# ------------
# tail -f mode
# ------------

# Find the size of the Tweets queue file and move to the end
st_results = os.stat(filename)
st_size    = st_results[6]
file.seek(st_size)
print "system     : Seek to end of Tweets queue : " + filename

# Find the size of the Netflow file and move to the end
st_resultsNetflow = os.stat(netflowFilename)
st_sizeNetflow    = st_resultsNetflow[6]
netflowFile.seek(st_sizeNetflow)
print "system     : Seek to end of Netflow file : " + netflowFilename

# Find the size of the System events/errors file and move to the end
st_resultsSyslog = os.stat(syslogFilename)
st_sizeSyslog    = st_resultsSyslog[6]
syslogFile.seek(st_sizeSyslog)
print "system     : Seek to end of errors file : " + syslogFilename

# Find the size of the Kippo events/errors file and move to the end
st_resultsKippo = os.stat(kippoFilename)
st_sizeKippo    = st_resultsKippo[6]
kippoFile.seek(st_sizeKippo)
print "system     : Seek to end of Kippo log file : " + kippoFilename

# Find the size of the DNS file and move to the end
st_resultsDns = os.stat(dnsFilename)
st_sizeDns    = st_resultsDns[6]
dnsFile.seek(st_sizeDns)
print "system     : Seek to end of DNSmasq log file : " + dnsFilename

# Find the size of the Telnetd file and move to the end
st_resultsTelnet = os.stat(telnetFilename)
st_sizeTelnet    = st_resultsTelnet[6]
telnetFile.seek(st_sizeTelnet)
print "system     : Seek to end of fake telnetd log file : " + telnetFilename

try:
    while True:        
    
        # look for events in Tweets queue
        # -------------------------------
        where = file.tell()
        line  = file.readline().rstrip()
        l     = len(line)
        
        if (l > 0 and l <= 3) :		# caused by AMUN logs - need to fix at source but this adds some protection
            print "Short line read, len=" + `l` + " so ignore..."
        elif not line :			# no data to process
            #print "kojoney_statd.py : nothing in Tweets queue to process"          
            file.seek(where)
        else:
            print "kojoney_statd.py : Tweet : "  + line                    
            tweet = line.split("tweet=")[1]
            tweet = tweet.strip('"')
            print "**** kojoney_statd.py tweet=" + tweet
            
            # Unlike Tweets, SNMP stats are based on uncorrelated events
            database = shelve.open(snmpoidsShelfFile)
            updateSnmpOIDs(database,line)
            database.close()
        
        # look for events in syslog messages file
        # ---------------------------------------
        whereSyslog = syslogFile.tell()
        lineSyslog  = syslogFile.readline().rstrip()
        if lineSyslog :
            #print "kojoney_statd.py : Syslog : " + lineSyslog
            database = shelve.open(snmpoidsShelfFile)
            updateSnmpOIDsErrors(database,lineSyslog)
            database.close()
        #else:
        #    print "kojoney_statd.py : nothing in syslog messages log to process"     
        
        # look for events in Netflow file
        # -------------------------------
        whereNetflow = netflowFile.tell()
        lineNetflow  = netflowFile.readline().rstrip()
        if lineNetflow :
            #print "kojoney_statd.py : Netflow : " + lineNetflow
            database = shelve.open(snmpoidsShelfFile)
            updateSnmpOIDsNetflow(database,lineNetflow)
            database.close()
        
        # look for events in Kippo file
        # -----------------------------
        whereKippo = kippoFile.tell()
        lineKippo  = kippoFile.readline().rstrip()
        if lineKippo :
            #print "kojoney_statd.py : Kippo : " + lineKippo
            database = shelve.open(snmpoidsShelfFile)
            updateSnmpOIDsKippo(database,lineKippo)
            database.close()
        
        # look for events in DNS file
        # ---------------------------
        wheredns = dnsFile.tell()
        lineDns  = dnsFile.readline().rstrip()
        if lineDns :
            #print "kojoney_statd.py : DNSmasq : " + lineDns
            database = shelve.open(snmpoidsShelfFile)
            updateSnmpOIDsDns(database,lineDns)
            database.close()
        
        # look for events in Telnetd file
        # -------------------------------
        whereTelnet = telnetFile.tell()
        lineTelnet  = telnetFile.readline().rstrip()
        if lineTelnet :
            #print "kojoney_statd.py : Telnetd : " + lineTelnet
            database = shelve.open(snmpoidsShelfFile)
            updateSnmpOIDsTelnet(database,lineTelnet)
            database.close()
                                    
        # delay
        # -----                                
        time.sleep(0.2)		

except Exception,e:
        
        print "kojoney_statd.py : main() exception caught = " + `e` + " line=" + line
        syslog.syslog("kojoney_statd.py : main() exception caught = " + `e` + " line=" + line)
