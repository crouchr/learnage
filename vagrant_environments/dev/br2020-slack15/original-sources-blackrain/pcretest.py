#!/usr/bin/python
import re
import getSnortInfo

#line = 'Jan  5 15:11:58 mars psad: src: 195.171.3.69 signature match: "SHELLCODE x86 inc ebx NOOP" (sid: 1390) tcp port: 445 fwsnort chain: FWSNORT_INPUT rule: 682'
line = 'Jan  5 15:11:58 mars psad: src: 195.171.3.69 signature match: "SHELLCODE x86 inc ebx NOOP" (sid: 1390) tcp port: 445 FWSNORT_INPUT rule: 682'


# snort sid
pat = "\[[0-9]:([0-9]*):[0-9]*"


# psad
pat = "signature match: \"([A-Za-z0-9 ]*)\""
a = re.findall(pat,line)
print "signature is " + a[0]

pat = "fwsnort chain: ([A-Z_]*)"
a = re.findall(pat,line)
if len(a) != 0 :
    print "fwsnort chain is " + a[0]

pat = "sid: (\d+)"
a = re.findall(pat,line)
sid = a[0]
print "sid is " + sid
                                    
classtype = getSnortInfo.getFwsnortAtom(sid,"classtype")
print "classtype is " + classtype

reference = getSnortInfo.getFwsnortAtom(sid,"reference")
print "reference is " + reference                                                