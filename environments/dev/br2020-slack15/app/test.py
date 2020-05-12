#!/usr/local/bin/python

import traceroute_matrix



a = traceroute_matrix.traceroute("HPOT","3.3.3.3",30)

path = '->'.join(a)
#print "result=" + a.__str__()
print "result=" + path.__str__()

