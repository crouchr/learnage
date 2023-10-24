#!/usr/bin/python

import syslog,sys,os

# $ whois -h hash.cymru.com e1112134b6dcc8bed54e0e34d8ac272795e73d74
# e1112134b6dcc8bed54e0e34d8ac272795e73d74 1221154281 53
def cymruHash(md5):
    try:
        cmd = "whois -h hash.cymru.com " + md5
        pipe = os.popen(cmd,'r')
        raw = pipe.read().rstrip("\n")
        #print raw
        a = raw.split(" ")
        print a
        
        if "NO_DATA" in raw :
            return "0"		# not seen by their AV 
        elif len(a) == 3 :
            return a[2]		# % of AV systems picking up the malware
        else:  			# what is this use case ?  
            return None
    except Exception,e:
        syslog.syslog("kojoney_cymru_hash.py:cymruHash() : " + e.__str__())
        return None
        

if __name__ == '__main__' :
    a = cymruHash("e1112134b6dcc8bed54e0e34d8ac272795e73d74")
    print a

    a = cymruHash("e1112134333cc8bed54e0e34d8ac272795e73d74")
    print a
        
#$ whois -h hash.cymru.com e1112134b6dcc8bed54e0e34d8ac272795e73d74
#e1112134b6dcc8bed54e0e34d8ac272795e73d74 1221154281 53