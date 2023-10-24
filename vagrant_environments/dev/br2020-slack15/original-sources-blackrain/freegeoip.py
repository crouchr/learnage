
import simplejson
import urllib2
import time
import socket

# u=http://freegeoip.net/json/8.8.8.8
# {'city': 'Mountain View', 'region_code': 'CA', 'region_name': 'California', 'areacode': '650', 'ip': '8.8.8.8',
# 'zipcode': '94043', 'longitude': -122.0574, 'metro_code': '807', 'latitude': 37.419199999999996, 'country_code': 'US', 'country_name': 'United States'}
def freegeoip(ip):
    try:
    
        u = 'http://freegeoip.net/json/' + ip
        #print "u=" + u
        socket.setdefaulttimeout(5)                                                                                                                   
        
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        headers = {'User-Agent' : user_agent}
                                                                                                                                    
        req = urllib2.Request(u,None,headers) 
        time.sleep(1)	# 4000 requests per hour are permitted                                                                                                                                 
        return simplejson.load(urllib2.urlopen(req))
    
    except urllib2.HTTPError,e:
        print "HTTP error " + e.__str__()
        return None
    except urllib2.URLError,e:
        print "URL error " + e.__str__()
        return None
    except Exception,e:
        print "freegeoip() : exception " + e.__str__()
        return None    
        
if __name__ == '__main__':
    ip = "8.8.8.8"
    results = freegeoip(ip)
    print results.__str__()
    if results != None:
        print results['country_code']
#
#      Searches the public timeline for the q string. There is no sanity checking
#      of the parameters. It's all passed straight to the API. Spec defined here:
#                
#      http://apiwiki.twitter.com/Twitter-Search-API-Method:+search
#                        
#      If you send refresh_url then all parameters are ignored. Example usage:
#                               
#      search_public_timeline('menendez')
#      search_public_timeline('menendez', since='2010-04-15')
#                                           
#      Ed Menendez - ed@menendez.com
#                                                    
#      >>> len(search_public_timeline('the')['results']) > 1
#      True
#      '''
                                                                                                                                            