#!/usr/bin/python

import time, os , syslog , re 

#Genre    : SymbianOS
#Details  : 6048 (Nokia 7650?)
#Distance : 37 hops
#Link     : ethernet/modem
#M-Score  : 0% (flags 0).
#Uptime   : 180654 hrs	/ if Linux

def getp0f(srcIP,dstIP,dstPort):

    try :
        p0f = {}

        #print "kojoney_p0f_lib.py : getp0f() : entered"
        cmd = "/usr/local/bin/p0fq /var/tmp/p0f_sock " + srcIP + " 0 " + dstIP + " " + dstPort
        #print "cmd = " + cmd.__str__()
        pipe = os.popen(cmd,'r')
        raw  = pipe.read() 
        raw  = raw.rstrip("\n") 
        #print "getp0f() : raw = " + raw.__str__()      
        
        if "Link" not in raw:	# if see "Link" then assume entry exists
            return None

        if "Genre and OS details not recognized" in raw:
            return None
        
        pat = "Genre\s+: (\w+)"
        genre = re.findall(pat,raw)
        #print "genre=" + genre.__str__()
        p0f['genre'] = genre[0]
        if p0f['genre'] == "Windows":	# genre key is used in mySQL so do not tinker with it
            p0f['genre_short'] = "WIN"	# genre_short is only used in Tweets so can fiddle with it
        elif p0f['genre'] == "Linux":
            p0f['genre_short'] = "LNX"
        elif p0f['genre'] == "Novell":
            p0f['genre_short'] = "NOVELL"
        else:
            p0f['genre_short'] = p0f['genre']
        
        pat = "Link\s+: (\w+)"
        link = re.findall(pat,raw)
        if len(link) > 0:
            p0f['link'] = link[0]
        else:
            p0f['link'] = "unknown"
        
        # This is only present if the OS is not UNKNOWN
        pat = "Distance\s+: (\d+) hops"
        hops = re.findall(pat,raw)
        if len(hops) > 0:
            #print "hops=" + hops.__str__()
            p0f['hops'] = hops[0]
        else:
            p0f['hops'] = "?"
        
        pat = "Uptime\s+: (\d+) (\w+)"
        uptime = re.findall(pat,raw)
        #print uptime
        if len(uptime) > 0:
            a,b = uptime[0]
            #print a
            #print b
            #if b == 'hrs' and int(a) > 100 :
            #    a = a / 24
            #    b = 'days'
            p0f['uptime'] = a + " " + b
        else:
            p0f['uptime'] = "N/A"
        #print "uptime=" + uptime.__str__()

        # Shorten for Twitter 
        #p0f['genre'].replace("Windows","Win32")
        #p0f['link'].replace("Ethernet/modem","Eth")
        print "getp0f() returns : " + p0f.__str__()
        
        return p0f
        
    except Exception,e:
        msg = "kojoney_p0f_lib.py : getp0f() : exception : " + e.__str__() + " " + line 
        syslog.syslog(msg)
        print msg
        return None

# TEST HARNESS
if __name__ == '__main__' :

    print "Started"
    
    # Test 1 - modify - e.g. use GRC shields up
    # =========================================
    #120.33.99.226:38715 - Linux 2.6, seldom 2.4 (older, 4) (up: 180654 secs) -> 192.168.1.60:6004
    print "Test 1"
    srcIP = "120.33.99.226"
    dstIP = "192.168.1.60"
    dstPort = "6004"
    
    p0fDict = getp0f(srcIP,dstIP,dstPort)
    
    if p0fDict != None:
        print "p0fDict : " + p0fDict.__str__()
    else:
        print "Failed to determine p0fDict"
    
    # Test 2 - GRC shields up
    # =======================
    print "Test 2"
    srcIP = "4.79.142.206"
    dstIP = "192.168.1.60"
    dstPort = "18080"
    
    p0fDict = getp0f(srcIP,dstIP,dstPort)
    
    if p0fDict != None:
        print "p0fDict : " + p0fDict.__str__()
    else:
        print "Failed to determine p0fDict"
    
    # Test 3 - always fail
    # ====================
    print "Test 3"
    srcIP = "1.1.1.1"
    dstIP = "192.168.1.60"
    dstPort = "18080"
    
    p0fDict = getp0f(srcIP,dstIP,dstPort)
    
    if p0fDict != None:
        print "p0fDict : " + p0fDict.__str__()
    else:
        print "Failed to determine p0fDict"
        
    # Test 4 - Mac Mini
    # =================
    print "Test 4 - Macmini"
    srcIP = "192.168.1.75"
    dstIP = "192.168.1.60"
    dstPort = "54"
    
    p0fDict = getp0f(srcIP,dstIP,dstPort)
    
    if p0fDict != None:
        print "p0fDict : " + p0fDict.__str__()
    else:
        print "Failed to determine p0fDict"
        
                                                                                                                                                                                                                   