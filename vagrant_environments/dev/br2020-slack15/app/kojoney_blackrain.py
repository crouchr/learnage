#!/usr/bin/python

import logging
import syslog
import time
import ipintellib	# rch library

from ConfigParser import ConfigParser

import p0fcmd
import BlackRainClient
import kojoney_hpot_mapping

sequence = 0

Brapi = None
SensorId = None

def loginToBRX(sensorId):
    global Brapi
    global SensorId
    SHORT_SLEEP = 1	# 5
    LONG_SLEEP  = 1  	# 60 seconds
    ATTEMPTS	= 1 	# 2
    
    SensorId = sensorId
    
    try :
        # Read configuration parameters from Blackrain config file
        config = ConfigParser()
        config.read("/etc/blackrain.conf")
        brxName = config.get('brx','brxName')
        brxIP   = config.get('brx','brxIP')
        brxPort = config.get('brx','brxPort')
        
        # Lookup IP using /etc/hosts file first (local override for testing)
        a = "BRX DNS name     : " + brxName.__str__()

        logging.info(a)
       # print a
        
        a = "BRX IP           : " + brxIP.__str__()
        logging.info(a)
        #print a
        
        a = "BRX port number  : " + brxPort.__str__()
        logging.info(a)
        #print a
 
        for i in range(ATTEMPTS) :	# 2 attempts
                    
            # Establish a session to BRX
            start = time.time()
            Brapi = BlackRainClient.BlackrainAPI(brxIP,brxPort,sensorId)            # hard-coded sensorID
            end = time.time()
            apiTime = end - start
            logging.info("BRAPI version v" + Brapi.get_version().__str__())
                
            #print "i=" + i.__str__() + " : establishing session to BlackRain Mothership @ " + brxIP + ":" + brxPort + "..."
            responseFromBrapi = Brapi.establish_session()
                                                             
            if responseFromBrapi != BlackRainClient.Status.ACCESS_SUCCESS:
                a = "[+] Warning : loginToBRX() FAILED attempt = " + i.__str__() + ", response = " + responseFromBrapi.__str__() + " BRX_LOGIN_PERF : %.2f" % apiTime + " secs" 
                #print a
                #logging.critical(a)
                #syslog.syslog(a)
                #print "Waiting..."
                if i == 0 :
                    time.sleep(SHORT_SLEEP)	# on first failure, use  short wait
                else :
                    time.sleep(LONG_SLEEP)	# wait 60 seconds - probably a persistent failure now
                continue		# have another attempt
            else :
                a = "[+] loginToBRX() OK : response = " + responseFromBrapi.__str__() +  " BRX_LOGIN_PERF : %.2f" % apiTime + " secs"
                #print a
                logging.info(a)
                #syslog.syslog(a)
                return 
            
        #    return 
        
        # Retry schedule expired
        #syslog.syslog("BRX_LOGIN_ERROR : Failed to login to BRX")
        return 
            
    except Exception , e :                                                                                             
        #logging.critical("Exception : kojoney_blackrain.loginToBRX() : " + e.__str__())  
        return 

def sendEvent(flowEvent) :
    global sequence
    eventHeader  = {}
    eventPayload = {}
        
    try :
        sequence = sequence + 1		# This will become obsolete in next version of API    
        #print flowEvent['flowType']
                
        if (flowEvent['flowType'] == "FLOW_HONEYD_FLOW" or flowEvent['flowType'] == "FLOW_NETFLOW_V5"): 
            eventHeader['flowType']       = flowEvent['flowType']
            eventHeader['flowRemoteIP']   = flowEvent['flowRemoteIP']
            eventHeader['flowRemotePort'] = flowEvent['flowRemotePort']
            eventHeader['flowHpotIP']     = flowEvent['flowHpotIP']
            eventHeader['flowHpotPort']   = flowEvent['flowHpotPort']
            eventHeader['flowProto']      = flowEvent['flowProto']
            eventHeader['flowDNS']        = flowEvent['flowDNS']
            eventHeader['flowCC']         = flowEvent['flowCC']
            eventHeader['flowCity']       = flowEvent['flowCity']
            eventHeader['flowLat']        = flowEvent['flowLat']
            eventHeader['flowLong']       = flowEvent['flowLong']
            eventHeader['flowASN']        = flowEvent['flowASN']
            eventHeader['flowISP']        = flowEvent['flowISP']
            eventHeader['flowRoute']      = flowEvent['flowRoute']
            eventHeader['flowRIR']        = flowEvent['flowRIR']
            eventHeader['seqNo']          = sequence		# in next version of API, this field will be handled by the API not application  
         
            eventPayload['hPotMsg']       = "-"			# Will contain log entry line
            eventPayload['hPotURL']       = "-"  		# E.g. for Web-based Honeypot such as Glastopf
            
            #eventPayload['hPotOther']     = flowEvent['flowDirection']	# temporary fix until db schema is fixed
            eventPayload['hPotOther']     = "-"			# Will contain captured Malware
        
        # Determine honeypot type based on hpot IP addtress
        #a,b = kojoney_hpot_mapping.getHpotIP(flowEvent['flowHpotIP'])
        a = kojoney_hpot_mapping.getHpotIP(flowEvent['flowHpotIP'])
        eventPayload['hPotType']      = a	# Text, note variable b is now ignored
        eventPayload['hPotID']        = flowEvent['flowDirection']

        if flowEvent['flowDirection'] == "in" :
            p0fInfo = p0fcmd.getP0fInfo(flowEvent['flowRemoteIP'],"0",flowEvent['flowHpotIP'],flowEvent['flowHpotPort'])
            if p0fInfo['result'] == True :           # p0f data is available
                eventHeader['flowOS'] = p0fInfo['genre']
            else :
                eventHeader['flowOS'] = '-'    
        else :
            eventHeader['flowOS'] = "-"
         
        #if flowEvent['flowType'] == "FLOW_NETFLOW_V5" :
        #    eventPayload['hPotType']      = "NETFLOW"
        #    eventPayload['hPotID']        = "0"
        #
        #elif flowEvent['flowType'] == "FLOW_HONEYD_FLOW" :
        #    eventPayload['hPotType']      = "HONEYD"
        #    eventPayload['hPotID']        = "1"
        #else :
        #    eventPayload['hPotType']      = "OTHER"		# This is actually an error
        #    eventPayload['hPotID']        = "-1"
        
        # Add Netflow-specific fields
        # RCH - not sure why this is here - mysql database does not have these fields
        if flowEvent['flowType'] == "FLOW_NETFLOW_V5" :
            eventHeader['flowDuration']        = flowEvent['flowDuration']
            eventHeader['flowPkts']            = flowEvent['flowPkts']
            eventHeader['flowBytes']	       = flowEvent['flowBytes']
            eventHeader['flowTflags']          = flowEvent['flowTflags']
            
        #print eventHeader.__str__()
        #print eventPayload.__str__()
        
        transmitToBRX(eventHeader, eventPayload)
        
        return

    except Exception,e:
        msg = "Exception : kojoney_blackrain.sendEvent() : " + e.__str__()
        print msg
        logging.critical(msg)
        return  

# Manage the retry schedule for sending the data to the BRX
def transmitToBRX(eventHeader,eventPayload):
    try :
        msg = "kojoney_blackrain.transmitToBRX() Header = " + eventHeader.__str__()
        logging.info(msg)
        #print msg
        
        msg = "kojoney_blackrain.transmitToBRX() Payload = " + eventPayload.__str__()
        logging.info(msg)	
        #print msg
        
        # Have 2 attempts to send the data to BRX
        for i in range(2) :
            start = time.time()
            responseFromBrapi = Brapi.push_event_details(eventHeader, eventPayload)
            end = time.time()
            apiTime = end - start
            
            if responseFromBrapi == BlackRainClient.Status.ACCESS_SUCCESS :
                msg = 'Brapi.push_event_details() call OK : ' + responseFromBrapi.__str__() + " BRX_EVENT_PERF : %.2f" % apiTime + " secs, attempt=" + i.__str__()
                logging.info(msg)	
                #print msg
                #syslog.syslog(msg)
                return 
            else :
                msg = 'Brapi.push_event_details() call WARNING : ' + responseFromBrapi.__str__()  + " BRX_EVENT_PERF : %.2f" % apiTime + " secs, attempt=" + i.__str__() 
                logging.info(msg)	
                #print msg
                #syslog.syslog(msg)
                #print "Waiting..."
                if i == 0 :
                    time.sleep(1)		# On first failure, short wait
                    loginToBRX(SensorId)
                else :
                    time.sleep(2)		# Backoff for longer on subsequent failure
        
        # Retry schedule expired
        #syslog.syslog("BRX_TX_ERROR : Failed to transmit data to BRX")
        return 
    
    except Exception,e:
        msg = "Exception : kojoney_blackrain.transmitToBRX() : " + e.__str__()
        print msg
        logging.critical(msg)
        syslog.syslog(msg)
        return  

