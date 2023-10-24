# Virustotal API class
# See API docs @ http://www.virustotal.com/advanced.html for the API reference.
# Usage:
#  api = VirusTotalAPI(my_api_key)
# API methods can be called like python functions:
#  data = api.get_file_report(resource=RESOURCE_ID)
# API methods return python objects (Or an exception)
#  print data["permalink"]
# All the API functions take the API arguments as their kwargs.
# The API key is automatically sent with the 
#
# Uploading a file requires the 'posthandler' module - if it is not
# available then the scan_file function will not work, but the rest
# of the API class will work.

import simplejson
import urllib
import urllib2
import functools
import urlparse
import syslog
import time
import kojoney_bitly

VT_API_KEY = "20e3d1e5da7681473a2d96563129bb189ab80e8159a1d714b220fce6f7629b82"

VT_DELAY = 20		# Use 2 if testing else use 20 : delay in seconds => API allows only 4 requests per second

try:
    import posthandler
    post_opener = urllib2.build_opener(posthandler.MultipartPostHandler)
except ImportError:
    posthandler = None
                          
class ModuleNotFound(Exception):
  ''' Module has not been found '''
                                   
class VirusTotalAPI(object):
    api_url = "https://www.virustotal.com/api/"
    api_methods = ["get_file_report","get_url_report","scan_url","make_comment"]  # Generic dynamic property methods (_call_api)
    special_methods = ["scan_file"] # Methods with their own function
                                                           
    def __init__(self, api_key):
        self.api_key = api_key
        for method in self.api_methods:
            setattr(self, method, functools.partial(self._call_api,method,key=self.api_key))
        for smethod in self.special_methods:
            setattr(self, smethod, functools.partial(getattr(self,"_special_"+smethod),key=self.api_key))
                                                                                                            
    def _call_api(self, function, **kwargs):
        url = self.api_url + function + ".json"
        data = urllib.urlencode(kwargs)
        req = urllib2.Request(url,data)
        returned = urllib2.urlopen(req).read()
        return simplejson.loads(returned)
                                                                                                                                              
    def _special_scan_file(self, **kwargs):
        if not posthandler:
            raise ModuleNotFound("posthandler module needed to submit files")
        json = post_opener.open(self.api_url + "scan_file.json",kwargs).read()
        return simplejson.loads(json)

# my wrapper functions ==============================================================================
        
def getVirusTotalUrl(url,vendor,dump=False):
    try:
        global VT_API_KEY
        global VT_DELAY
        
        time.sleep(VT_DELAY)
        
        #print "getVirusTotalUrl() : url = " + url.__str__()
        
        api=VirusTotalAPI(VT_API_KEY)
    
        resultURL = api.get_url_report(resource=url)
        print "resultURL=" + resultURL.__str__()
        apiStatus = resultURL['result']
        if apiStatus == 0 :	
            return "CLEAN"	        
        elif apiStatus == 1 :
            pass
        else:
            return "VT_API_ERR " + apiStatus.__str__()	# -2 = too many submissions per minute (4 / min max)     
        
        filescan_id = resultURL['filescan_id'].__str__()
        print "*** filescan_id : " + filescan_id
            	        
        a = resultURL['report']
        dateFirstSeen = a[0]
        #print "dateFirstSeen : " + dateFirstSeen.__str__()

        b = a[1]
    
        matches = 0
        total  =  0
        result = "ERROR"
          
        if vendor == "ALL":
            for vendor in b:
                total = total + 1
                if dump == True:
                    print vendor + " : " + b[vendor]
                if b[vendor] == "malicious site" :
                    matches = matches + 1
            # code join
            result = matches.__str__() + "/" + total.__str__()
        else:
            result = b[vendor]
        
        if result == None :
            result = "OK"
        elif len(result) == 0 :
            result = "OK"
          
        return result
        
    except Exception,e:
        msg = "getVirusTotalURL() : exception : " + e.__str__()
        syslog.syslog(msg)
        print msg
        return "ERROR"
        
# --------------------------------------------------      
# TODO :
# 1. Sort the list of vendors in alphabetical order
# 2. check if return code = 0 = "UNSEEN_BY_VT" 
# 
def getVirusTotalFile(malwareMD5,vendor,dump=False):
    try:
        global VT_API_KEY
        global VT_DELAY
        result = {}
        matchList = []
        
        time.sleep(VT_DELAY)
        
        result['matches']    = 0
        result['total']      = 0
        result['single']     = "ERROR"
        result['date']       = "ERROR"
        result['permalink']  = "ERROR"
        result['bitly']      = "ERROR"
        result['md5']        = malwareMD5
        result['summary']    = "ERROR"
                
        #print "getVirusTotalFile() : malwareMD5 = " + malwareMD5.__str__()
        
        api=VirusTotalAPI(VT_API_KEY)
    
        resultMalware = api.get_file_report(resource=malwareMD5)
        print "resultMalware=" + resultMalware.__str__()
        apiStatus = resultMalware['result']
        if apiStatus == 0 :	# not found in VT database
            result['data']    = "Unseen by VirusTotal"
            result['single']  = "Unseen by VirusTotal"
            result['summary'] = "Unseen by VirusTotal"
            result['status'] = True
            return result	        
        elif apiStatus == 1 :	# found in VT database
            pass
        else:			# everything else assumed an error
            result['status'] = False
            result['data']   = "VT_API_ERR " + apiStatus.__str__()		# -2 = too many submissions per minute (4 / min max)     
            return result
            
        result['status'] = True
        result['permalink'] = resultMalware['permalink']
        result['bitly'] = kojoney_bitly.getBitly(result['permalink'])
         
        a = resultMalware['report']
        result['date'] = a[0]
        
        
        b = a[1]
    
        matches = 0
        total  =  0
        #result = "ERROR"
        #c = {}
          
        if vendor == "ALL":
            for vendor in b :
                total = total + 1
                #if dump == True:
                #    print vendor + " : " + b[vendor]
                if len(b[vendor]) != 0 :
                    c = {}
                    #matchList.append((vendor,b[vendor]))	# add tuple
                    c[vendor] = b[vendor]
                    matchList.append(c)
                    matches = matches + 1
                    if dump == True:
                        print vendor + " : " + b[vendor]
            # code join
            #result['matches'] = matches.__str__() + "/" + total.__str__()
        else:
            c = {}
            c[vendor] = b[vendor]
            matchList.append(c)
            #result = b[vendor]
            
        result['data']    = matchList
        result['matches'] = matches
        result['total']   = total
        
        # Choose single result with one of the following prefered AV vendors
        #print "SINGLE -------------"
        #result['single'] = result['data'][0].__str__()
        i = result['data'][0]
        #print i
        for a in i :
            result['single'] = a + "=" + i[a]
        #print result['single']
        
        if result['matches'] > 0 :
            for i in result['data']:
                #print i
                if i.has_key("Kaspersky"):
                    result['single'] = "Kaspersky" + "=" + i['Kaspersky']
                    break
                elif i.has_key("Symantec"):
                    result['single'] = "Symantec" + "=" + i['Symantec']
                    break
                elif i.has_key("Norman"):
                    result['single'] = "Norman" + "=" + i['Norman']
                    break
                elif i.has_key("TrendMicro"):
                    result['single'] = "TrendMicro" + "=" + i['TrendMicro']
                    break
                elif i.has_key("Ikarus"):
                    result['single'] = "Ikarus" + "=" + i['Ikarus']
                    break    
                    
        #print "SINGLE : " + result['single']    
        
        #if result == None :
        #    result = "OK"
        #elif len(result) == 0 :
        #    result = "OK"
        
        result['summary'] = result['single'] + " " + result['matches'].__str__() + "/" + result['total'].__str__() + " VT=" + result['bitly'] 
          
        return result
        
    except Exception,e:
        msg = "getVirusTotalFile() : exception : " + e.__str__()
        syslog.syslog(msg)
        print msg
        result['status'] = False
        result['data'] = e.__str__()
        return result

def test():
    try:
        filename = '/home/var/log/kojoney_analyst.txt'
        fp = open(filename,'r')
          
        print "virustotal.py : Seek to START of Analyst Job file " + filename
                                                                                                                        
        while True:
            line  = fp.readline().rstrip()
            fields = line.split(',')
            
            #if fields[1] == "URL" :
            #    print "-----------------------------------------------------------------------------------"
            #    print "URL line : " + line
            #    url = fields[2]
            #    vtMatches = getVirusTotalUrl(url,"ALL",True)
            #    print " "
            #    print " -> return = " + vtMatches.__str__()
            #    print " "
                
            if fields[1] == "PHPFILE" :
                print "-----------------------------------------------------------------------------------"
                print "FILE line : " + line
                malwareMD5 = fields[2]
                result = getVirusTotalFile(malwareMD5,"ALL",True)
                print " " 
                print result['status']
                if result['status'] == True:
                    print result['md5']
                    #print result['data']
                    print result['date']
                    print result['single']
                    print result['matches']
                    print result['total']
                    print result['permalink']
                    print result['bitly']
                    print "Summary : " + result['summary']
                print " "
                
    except Exception,e:
        msg = "test() : exception : " + e.__str__()
        syslog.syslog(msg)
        print msg
        return "ERROR"
                                                                                                                                                                                                         
if __name__ == '__main__' :
    print " "
    syslog.openlog("virustotal")
    syslog.syslog("Started, entry point = test()")
    test()
else:    
    print " "
    syslog.openlog("virustotal")
    syslog.syslog("Started")
    pass
    # -------------
    # FILE scanning
    # -------------
     
    #malwareMD5 = "6cae055435fa957fba2698e98228954a"    
    #vendor = "ALL"
    #vtMatches = getVirusTotalFile(malwareMD5,vendor,True)
    #print vendor + " : " + vtMatches.__str__()
    #print " "    
    
    # Made up MD5
    #malwareMD5 = "11111111111111111111111111111111"
    #vendor = "ALL"
    #vtMatches = getVirusTotalFile(malwareMD5,vendor,True)
    #print vendor + " : " + vtMatches.__str__()
    #print " "    

    #malwareMD5 = "e08987cadf4bd5ca7ffb45ee8056aaa3"
    #vendor = "ALL"
    #vtMatches = getVirusTotalFile(malwareMD5,vendor,True)
    #print vendor + " : " + vtMatches.__str__()
    #print " "    
    
    #vendor = "ClamAV"
    #vtMatches = getVirusTotalFile(malwareMD5,vendor,False)
    #print vendor + " : " + vtMatches.__str__()
    
    #vendor = "Norman"
    #vtMatches = getVirusTotalFile(malwareMD5,vendor,False)
    #print vendor + " : " + vtMatches.__str__()

    #vendor = "Kapersky"
    #vtMatches = getVirusTotalFile(malwareMD5,vendor,False)
    #print vendor + " : " + vtMatches.__str__()
    
    #vendor = "Symantec"
    #vtMatches = getVirusTotalFile(malwareMD5,vendor,False)
    #print vendor + " : " + vtMatches.__str__()
    
    # ------------
    # URL scanning
    #  ------------
    
    #url = "http://www.google.com"
    #vendor = "ALL"
    #vtMatches = getVirusTotalUrl(url,vendor,True)
    #print vendor + " : " + vtMatches.__str__()
    #print " "    

    #url = "http://www.openbsd.com"
    #vendor = "ALL"
    #vtMatches = getVirusTotalUrl(url,vendor,True)
    #print vendor + " : " + vtMatches.__str__()
    #print " "    
                                                                                                                                                                                                             