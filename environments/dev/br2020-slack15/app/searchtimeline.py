
import simplejson
import urllib

def search_public_timeline(q, refresh_url=None, **kwargs):
    if not refresh_url:
        parms = {}
        parms['q'] = q
        parms.update(kwargs)
        query_str = '?%s' % urllib.urlencode(parms)
    else:
        query_str = refresh_url
                                                                      
        u = 'http://search.twitter.com/search.json%s' % query_str
        print u
                                                                                                                   
        #user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        #headers = {'User-Agent' : user_agent}
                                                                                                                                    
        req = urllib2.Request(u) #, None, headers
                                                                                                                                     
        return simplejson.load(urllib2.urlopen(req))
        
        
if __name__ == '__main__':
    q = "botnet"
    q = "one direction"
    results = search_public_timeline(q,refresh_url=None)
    print results.__str__()
    
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
                                                                                                                                            