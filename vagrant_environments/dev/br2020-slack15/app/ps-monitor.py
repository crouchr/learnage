#!/usr/bin/python
import os,time,syslog,sys
import PreludeEasy

ProcessTable = {}

SENSOR_IP = "192.168.1.67"

def BuildCurrentProcessTable():
    global ProcessTable

    try:
        ProcessTable = {}	# zero the process table
    
        os.system("ps auxh > /tmp/processTable.txt")
        file = open("/tmp/processTable.txt",'r')
        
        while True:
            line = file.readline()
            line = line.strip()
            if not line :  
                #print "No (more) data to read"
                break
        
            #print "line is : " + line     
            fields=line.split()
            #print fields
            ps = ' '.join(fields[10:])
            #print "pre-ps  =" + ps.__str__()
            
            # Remove any scripting languages
            ps = ps.replace("/usr/bin/python -O","")	# special for Amun
            ps = ps.replace("/usr/bin/python ","")
            ps = ps.replace("python ","")
            
            ps = ps.replace("/usr/bin/perl ","")
            ps = ps.replace("perl ","")
            
            ps = ps.replace("/usr/bin/twistd -y","")	# special for Kippo
            ps = ps.replace("/usr/bin/twistd ","")
            
            ps = ps.replace("/bin/sh ","")
            
            ps = ps.lstrip()
            ps = ps.rstrip()
            
            #print "post1-ps=" + ps.__str__()
            
            # Extract just the command, no arguments
            ps = ps.split(" ")
            ps = ps[0]
            if len(ps) <= 0 :
                print "process shortened to zero length, so ignore : " + line
                continue	# next process
            #print "post2-ps=" + ps.__str__()
            
            cpu = fields[2]

            mem = fields[3]
            
            ###########################
            # Uncomment for debugging #
            ###########################
            #print "process = " + ps + " : " + "cpu = " + cpu + " : " + "mem = " + mem
            
            # 40.0 is good threshold valaue to use, 4.0 is good for triggering an event
            if float(cpu) > 60.0 :
                msg = "Warning ! : CPU_HOG : process [" + ps[0:64] + "]... running at CPU of " + cpu.__str__() + "%"
                #print msg
                addInfo = "CPU measured at " + cpu + " %"
                
                # maldet (bash) causes lots of triggers of this 
                if "/bin/bash" not in ps[0:64]:
                    sendMonitorIDMEF(SENSOR_IP,"Honeypot core process CPU hog",ps,addInfo)
                    syslog.syslog(msg)
                
            # suricata is biggest user of memory (40.0), 4.0 is good for triggering an event    
            if float(mem) > 40.0 :
                msg = "Warning ! : MEMORY_HOG : process [" + ps[0:64] + "]... memory consumption at " + mem.__str__() + "%"
                syslog.syslog(msg)
                print msg
                addInfo = "Memory consumption measured at " + mem + " %"
                sendMonitorIDMEF(SENSOR_IP,"Honeypot core process memory hog",ps,addInfo)
                    
            ProcessTable[ps] = cpu 
            #print "ps=" + ps.__str__() + ", cpu=" + cpu.__str__()
                   
        #print ProcessTable 
    
    except Exception,e:
        msg = "ps-monitor.py : buildCurrentProcessTable() exception caught = " + `e`
        syslog.syslog(msg)
        print msg
        sys.exit()            
  

def checkProcess(id,process,restartScript):
    global ProcessTable
    
    try:    
        if ProcessTable.has_key(process) :
            pass
        else:
            msg = "PROCESS_DIED : error : " + id + "=" + "[" + process[0:64] + "]..." + " NOT RUNNING, restart using " + restartScript
            print msg
            #print "[" + process + "]"
            
            result = os.system(restartScript + " & ")
            syslog.syslog(msg)
            sendMonitorIDMEF(SENSOR_IP,"Honeypot core process restarted",process)
            
    except Exception,e:
        syslog.syslog("ps-monitor.py : checkProcess() exception caught = " + `e`)
        sys.exit()            

# Works for all events monitored by ps-monitor
def sendMonitorIDMEF(sensorIP,text,processName,addInfo=None):
    try:
        
        # Create a new Prelude client.
        client = PreludeEasy.ClientEasy("blackrain")
        client.Start()
                            
        # Create the IDMEF message
        idmef = PreludeEasy.IDMEF()
                                           
        # Classification
        idmef.Set( "alert.classification.text", text)
                                                            
        # Source
        idmef.Set("alert.source(0).node.address(0).address", sensorIP)
                                                                            
        idmef.Set("alert.assessment.impact.severity", "medium")  
        idmef.Set("alert.assessment.impact.type", "other")
                
        idmef.Set("alert.source(0).process.name",processName)                
        
        if addInfo != None:
            idmef.Set("alert.additional_data(0).type", "string")
            idmef.Set("alert.additional_data(0).meaning", "info")
            idmef.Set("alert.additional_data(0).data", addInfo)
                         
        client.SendIDMEF(idmef)
        return
                       
    # example : sendMonitorIDMEF() : exception : TLS server certificate is NOT trusted.                                         
    except Exception,e:
        msg = "sendMonitorIDMEF() : exception : " + e.__str__()
        syslog.syslog(msg)
        print msg
        return
                                                         
# main ------

syslog.openlog("ps-monitor",syslog.LOG_PID,syslog.LOG_LOCAL2)         # Set syslog program name 

#WAITTIME = 5
WAITTIME = 60
msg = "ps-monitor.py : Waiting for initial delay of " + WAITTIME.__str__() + " seconds..."
print msg
syslog.syslog(msg)

time.sleep(WAITTIME)	

msg = "ps-monitor.py : Now monitoring core processes for availability and all processes for CPU & memory..."
syslog.syslog(msg)
print msg

# do not add command-line arguments to this
while True:
    try:    
        BuildCurrentProcessTable()

        checkProcess("kojoney_tweet_engine"    , "/home/crouchr/kojoney_tweet_engine.py"         , "/etc/rc.d/rc.kojoney_tweet_engine restart")
#        checkProcess("kojoney_statd"           , "/home/crouchr/kojoney_statd.py"                , "/etc/rc.d/rc.kojoney_statd restart")
#        checkProcess("attacker_statd"          , "/home/crouchr/attacker_statd.py"               , "/etc/rc.d/rc.attacker_statd restart")
#        checkProcess("kojoney_snmp_hpot"       , "/home/crouchr/kojoney_snmp_hpot.py"            , "/etc/rc.d/rc.kojoney_snmp_hpot restart")
        
#        checkProcess("faketelnetd"             , "/usr/local/src/faketelnetd/faketelnetd"        , "/etc/rc.d/rc.faketelnetd restart")
#        checkProcess("spamhole"                , "/usr/local/src/spamhole/spamhole"              , "/etc/rc.d/rc.spamhole restart")
        
#####        checkProcess("blackrain_netflow"       , "/home/crouchr/blackrain_netflow.pl"            , "/etc/rc.d/rc.kojoney_netflow start")
        
#        checkProcess("ossec-csyslogd"             , "/var/ossec/bin/ossec-csyslogd"                 , "/etc/rc.d/rc.ossec_csyslogd restart")
        checkProcess("kojoney_guru"               , "/home/crouchr/kojoney_guru.py"                 , "/etc/rc.d/rc.kojoney_guru restart")

#       checkProcess("twitter_streamer"           , "/home/crouchr/twitter_streamer.py"             , "/etc/rc.d/rc.twitter_streamer restart")

#        checkProcess("kojoney_ossec_syslogd"      , "/home/crouchr/kojoney_ossec_syslogd.py"        , "/etc/rc.d/rc.kojoney_ossec_syslogd restart")
#        checkProcess("kojoney_attacker_correlate" , "/home/crouchr/kojoney_attacker_correlate.py"   , "/etc/rc.d/rc.kojoney_attacker_correlate restart")
#        checkProcess("kojoney_tsom"               , "/home/crouchr/kojoney_tsom.py"                 , "/etc/rc.d/rc.kojoney_tsom restart")
        checkProcess("kojoney_logglyd"            , "/home/crouchr/kojoney_logglyd.py"              , "/etc/rc.d/rc.kojoney_logglyd restart")
        checkProcess("kojoney_alert"              , "/home/crouchr/kojoney_alert_server.py"         , "/etc/rc.d/rc.kojoney_alert restart")
        checkProcess("kojoney_anubis"             , "/home/crouchr/kojoney_anubis.py"               , "/etc/rc.d/rc.kojoney_anubis restart")
        checkProcess("kojoney_tweet"              , "/home/crouchr/kojoney_tweet.py"                , "/etc/rc.d/rc.kojoney_tweet restart")
        checkProcess("kojoney_defend"             , "/home/crouchr/kojoney_defend.py"               , "/etc/rc.d/rc.kojoney_defend restart")
#        checkProcess("kojoney_splunk_platform"    , "/home/crouchr/kojoney_splunk_platform.py"      , "/etc/rc.d/rc.kojoney_splunk_platform restart")
        #checkProcess("kojoney_suricata_syslog"   , "/usr/bin/python /home/crouchr/kojoney_suricata_syslog.py"      , "/etc/rc.d/rc.kojoney_suricata_syslog restart")

        #checkProcess("honeytrap"               , "/usr/local/sbin/honeytrap"                     , "/etc/rc.d/rc.honeytrap restart")
        #checkProcess("pads"                    , "/usr/local/bin/pads"                           , "/etc/rc.d/rc.pads restart")
        #checkProcess("tcpxtract"               , "/usr/local/bin/tcpxtract"                      , "/etc/rc.d/rc.tcpxtract restart")
        #checkProcess("passer"                  , "/usr/bin/python /home/crouchr/passer-v1.16.py -l /home/var/log/passer.csv","/etc/rc.d/rc.passer restart")
        #checkProcess("iplog"                   , "/usr/local/sbin/iplog -i eth0 --disable-resolver --log-ip --dns-cache=true --ignore -l /home/var/log/iplog.log","/etc/rc.d/rc.iplog restart")
        checkProcess("iplog"                   , "/usr/local/sbin/iplog"                         , "/etc/rc.d/rc.iplog restart")
        
        #checkProcess("p0f3"                    , "/usr/local/bin/p0f3"                           , "/etc/rc.d/rc.p0f restart")
        checkProcess("p0f2"                    , "/usr/sbin/p0f"                                 , "/etc/rc.d/rc.p0f2 restart")
        
        # Argus processes - restart both if either dies
        checkProcess("argus"                   , "/usr/local/sbin/argus"                         , "/etc/rc.d/rc.argus restart")
        checkProcess("ra"                      , "/usr/local/bin/ra"                             , "/etc/rc.d/rc.ra restart")
              
        #checkProcess("kojoney_twitter_drone"   , "/usr/bin/python /home/crouchr/kojoney_twitter_drone.py" , "/etc/rc.d/rc.kojoney_twitter_drone restart")        
        #checkProcess("kojoney_sec"           , "/usr/bin/perl -w /usr/local/bin/sec.pl ","/etc/rc.d/rc.sec restart")        
        #checkProcess("Sagan HIDS Snort Adapter"," /usr/local/sbin/sagan" , "/etc/rc.d/rc.sagan restart")
        
        # For some reason - not working
        #checkProcess("snort"                    ,"/usr/local/bin/snort -q -c /etc/snort/snort.conf -i eth0 --pid-path /var/run/rchpids --nolock-pidfile -D" , "/etc/rc.d/rc.snort restart")
                
        #checkProcess("test","/usr/local/bin/test" , "/etc/rc.d/rc.test")
    
        # force an exception for testing purposes
        #a = 1/0
        
        time.sleep(30)
    
    except Exception,e:
        syslog.syslog("ps-monitor.py : main() exception caught = " + `e`)
        sys.exit()
   
