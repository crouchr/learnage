import cookielib, urllib2, urllib, sys, logging

# python 2.6
#import json
# python 2.5
import simplejson as json

'''
Created on 20 Apr 2011

@author: mat rule

@file_version : 0.3
'''

VERSION="0.1"            # API version

class Status():
    CONNECTION_REFUSED = "CONNECTION_REFUSED"    # http connection refused by BRX
    ACCESS_DENIED      = "ACCESS_DENIED"    # credentials refused  by BRX
    ACCESS_SUCCESS     = "ACCESS_SUCCESS"    # credentials accepted by BRX
    SESSION_ERROR      = "SESSION_ERROR"    # HTTP JSession expired, or incorrect
    PUSH_OK            = "PUSH_OK"      # sensor info accepted by BRX
    PUSH_FAIL          = "PUSH_FAIL"    # sensor info refused  by BRX
    GENERAL_FAIL       = "GENERAL_FAIL"    # catchall error
    
class BlackrainAPI(object):
    '''
    classdocs
    '''
    server = "0.0.0.0"
    port = 1
    sensorId = "0000000000"
    user_agent = 'Rocknroll/1.0 (compatible; blackrainx)'
    post_headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
   
    
    def __init__(self, server, port, sensorId):
        self.server = server        # rch BRX IP address
        self.port = port
        self.sensorId = sensorId
        #TODO create a custom logger to share with Richards stuff...or receive custom logger from Richards parent class
        logging.basicConfig(level=logging.INFO,
              format='%(asctime)s %(name)-12s %(levelname)s: %(message)s',
              datefmt='%m-%d %H:%M:%S',
              filename='blackrainclient.log',
              filemode='w')
        
        try:
            cookie_jar = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
            urllib2.install_opener(opener)
            logging.info('Blackrainclient API class created')    # rch typo
            logging.info('Cookie Jar created')
        except:
            logging.critical(sys.exc_info())            
    
    def get_version(self):
        return VERSION
    
    def establish_session(self):
        url = 'http://'+self.server+':'+self.port+'/BlackRainXchange/DoLogin'
        logging.info("url = " + `url`)            # rch
        new_session_values = {'sensorId': self.sensorId}
        status=-1
        try:
            data = urllib.urlencode(new_session_values)
            req  = urllib2.Request(url, data, self.post_headers)
            response = urllib2.urlopen(req)
            responseBody = response.read()
            if "successful" in responseBody:
                status = Status.ACCESS_SUCCESS
                logging.info('Connection to:'+self.server+':'+self.port+' credentials ok')
            if "denied" in responseBody:
                status = Status.ACCESS_DENIED
                logging.info('Connection to:'+self.server+':'+self.port+' credentials denied')
        except:
            logging.critical('Establish session fail: ' + `sys.exc_info()`)    # rch
            status = Status.GENERAL_FAIL
            
        return status
    
    
    def push_registration_details(self,sensorRegistration):
        
        url = 'http://'+self.server+':'+self.port+'/BlackRainXchange/DoRegistration'
        register_values = {'sensorName':    sensorRegistration['sensorName'],
                           'sensorVersion':        sensorRegistration['sensorVersion'],
                           'sensorWanIP':          sensorRegistration['sensorWanIP'],
                           'sensorHoneypotIPList': sensorRegistration['sensorHoneypotIPList'],
                           'sensorNatType':        sensorRegistration['sensorNatType'],
                           'sensorSSL':            sensorRegistration['sensorSSL'],
                           'sensorBogomips':       sensorRegistration['sensorBogomips'],
                           'sensorIPCountryCode':  sensorRegistration['sensorIPCountryCode'],
                           'sensorIPCountryName':  sensorRegistration['sensorIPCountryName'],
                           'sensorIPCityName':     sensorRegistration['sensorIPCityName'],
                           'sensorIPLatitude':     sensorRegistration['sensorIPLatitude'],
                           'sensorIPLongitude':    sensorRegistration['sensorIPLongitude'],
                           'sensorIPASN':          sensorRegistration['sensorIPASN'],
                           'sensorIPASName':       sensorRegistration['sensorIPASName'],
                           'sensorIPDNS':          sensorRegistration['sensorIPDNS'],
                           'sensorDGiface':        sensorRegistration['sensorDGiface'],
                           'sensorDGmac':          sensorRegistration['sensorDGmac'],
                           'sensorBaseIPmethod':   sensorRegistration['sensorBaseIPmethod'],
                           'sensorRAM':            sensorRegistration['sensorRAM'],
                           'sensorCPUnum':         sensorRegistration['sensorCPUnum'],
                           'sensorCPUmodel':       sensorRegistration['sensorCPUmodel'],
                           'sensorCPUfreq':        sensorRegistration['sensorCPUfreq'],
                           'sensorCPUflags':       sensorRegistration['sensorCPUflags'],
                           'sensorCPUbogomips':    sensorRegistration['sensorCPUbogomips'],
                           'sensorCPUmemtotal':    sensorRegistration['sensorCPUmemtotal'],
                           'sensorCPUmemfree':     sensorRegistration['sensorCPUmemfree'],
                           'sensorPersonName':     sensorRegistration['sensorPersonName'],
                           'sensorPersonEmail':    sensorRegistration['sensorPersonEmail'],
                           'sensorUptime':         sensorRegistration['sensorUptime'] }
        
        logging.info(sensorRegistration)
        
        try:
            data = urllib.urlencode(register_values)
            req = urllib2.Request(url, data, self.post_headers)
            response = urllib2.urlopen(req)
            responseBody = response.read()
            if "successful" in responseBody:
                status = Status.PUSH_OK
                logging.info('Connection to:'+self.server+':'+self.port+' credentials ok')
            if "denied" in responseBody:
                status = Status.ACCESS_DENIED
                logging.info('Connection to:'+self.server+':'+self.port+' credentials denied')
            if "error in details" in responseBody:
                status = Status.PUSH_FAIL
                logging.info('Connection to:'+self.server+':'+self.port+' error with the details submitted')
        except:
            logging.critical('Push registration details fail: ' + `sys.exc_info()`) # rch
            status = Status.GENERAL_FAIL
        #'if session denied, then auto establish session again'
        
        return status
    
    def pull_registration_details(self):
                
        url = 'http://'+self.server+':'+self.port+'/BlackRainXchange/GetConfig'
        logging.info("url = " + `url`)            # rch
        new_session_values = {}
        status=-1
        response_dict = {}
        
        try:
            data = urllib.urlencode(new_session_values)
            req  = urllib2.Request(url, data, self.post_headers)
            response = urllib2.urlopen(req)
            responseBody = response.read()
            if "successful" in responseBody:
                status = Status.ACCESS_SUCCESS
                logging.info('Connection to:'+self.server+':'+self.port+' credentials ok')
            if "denied" in responseBody:
                status = Status.ACCESS_DENIED
                logging.info('Connection to:'+self.server+':'+self.port+' credentials denied')
        except:
            logging.critical('Establish session fail: ' + `sys.exc_info()`)    # rch
            status = Status.GENERAL_FAIL
            
        json_response = json.loads(responseBody)
        response_dict['sensorReportsEmail'] = json_response['sensorReportsEmail']
        response_dict['CONSUMER_KEY'] = json_response['CONSUMER_KEY']
        response_dict['CONSUMER_SECRET'] = json_response['CONSUMER_SECRET']
        response_dict['ACCESS_KEY'] = json_response['ACCESS_KEY']
        response_dict['ACCESS_SECRET'] = json_response['ACCESS_SECRET']
        
        for honey_application_detail in json_response['sensorHoneypotIPList']:
            response_dict[honey_application_detail.split('=')[0]] = honey_application_detail.split('=')[1]
        
        return response_dict
    
    def push_event_details(self, eventHeader, eventPayload):
        
        url = 'http://'+self.server+':'+self.port+'/BlackRainXchange/PushEvent'
        logging.info("url = " + `url`)            # rch
        push_event_values = {   'flowType':         eventHeader['flowType'],
                                'flowRemoteIP':     eventHeader['flowRemoteIP'],
                                'flowRemotePort':   eventHeader['flowRemotePort'],
                                'flowHpotIP':       eventHeader['flowHpotIP'],
                                'flowHpotPort':     eventHeader['flowHpotPort'],
                                'flowProto':        eventHeader['flowProto'],
                                'flowOS':           eventHeader['flowOS'],
                                'flowDNS':          eventHeader['flowDNS'],
                                'flowCC':           eventHeader['flowCC'],
                                'flowCity':         eventHeader['flowCity'],
                                'flowLat':          eventHeader['flowLat'],
                                'flowLong':         eventHeader['flowLong'],
                                'flowASN':          eventHeader['flowASN'],
                                'flowISP':          eventHeader['flowISP'],
                                'flowRoute':        eventHeader['flowRoute'],
                                'flowRIR':          eventHeader['flowRIR'],
                                'seqNo':            eventHeader['seqNo'], 
                                'hPotType':         eventPayload['hPotType'],
                                'hPotMsg':          eventPayload['hPotMsg'],
                                'hPotID':           eventPayload['hPotID'],
                                'hPotURL':          eventPayload['hPotURL'],
                                'hPotOther':        eventPayload['hPotOther'] }
        status=-1
        
        try:
            data = urllib.urlencode(push_event_values)
            req  = urllib2.Request(url, data, self.post_headers)
            response = urllib2.urlopen(req)
            responseBody = response.read()
            if "successful" in responseBody:
                status = Status.ACCESS_SUCCESS
                logging.info('Connection to:'+self.server+':'+self.port+' credentials ok')
            if "denied" in responseBody:
                status = Status.ACCESS_DENIED
                logging.info('Connection to:'+self.server+':'+self.port+' credentials denied')
        except:
            logging.critical('Establish session fail: ' + `sys.exc_info()`)    # rch
            status = Status.GENERAL_FAIL
            
        return status