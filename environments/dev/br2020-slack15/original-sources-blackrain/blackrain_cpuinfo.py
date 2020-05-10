#!/usr/local/bin/python
#
#crouchr@mars:~$ cat /proc/cpuinfo
#processor       : 0
#vendor_id       : GenuineIntel
#cpu family      : 6
#model           : 11
#model name      : Mobile Intel(R) Pentium(R) III CPU - M  1000MHz
#stepping        : 4
#cpu MHz         : 996.704
#cache size      : 512 KB
#fdiv_bug        : no
#hlt_bug         : no
#f00f_bug        : no
#coma_bug        : no
#fpu             : yes
#fpu_exception   : yes
#cpuid level     : 2
#wp              : yes
#flags           : fpu vme de pse tsc msr pae mce cx8 sep mtrr pge mca cmov pat pse36 mmx fxsr sse
#bogomips        : 1994.71
#clflush size    : 32

import os,syslog


def getCpuInfo():
    
    cpuinfo = {}
    
    cmdLine = "cat /proc/cpuinfo"
    #print "cmdLine = " + cmdLine 
             
    try:
        pipe = os.popen(cmdLine,'r')
        raw = pipe.read().rstrip("\n")
        #print raw
        raw=raw.replace("\n",":")
        
        #print " "
        #print raw
        
        start = raw.find("model name")
        cpuinfo['modelName'] = raw[start:].split(':')[1].lstrip(" ")
        
        start = raw.find("cpu MHz")
        cpuinfo['cpuMHz'] = raw[start:].split(':')[1].lstrip(" ")
        
        start = raw.find("bogomips")
        cpuinfo['bogomips'] = raw[start:].split(':')[1].lstrip(" ")
        
        start = raw.find("cache size")
        cpuinfo['cacheSize'] = raw[start:].split(':')[1].lstrip(" ")
        
        start = raw.find("flags")
        cpuinfo['cpuflags'] = raw[start:].split(':')[1].lstrip(" ")
        
        return cpuinfo
                                                                                                                                                                            
    except Exception,e:                                    
        syslog.syslog("Exception " + `e` + " in getCpuInfo(), raw=" + raw);
        return None
                                                                                                                                          

#root@br:/proc# cat meminfo 
#MemTotal:      1347660 kB
#MemFree:       1287360 kB
#Buffers:          9084 kB
#Cached:          25212 kB
#SwapCached:          0 kB
#Active:          15628 kB
#Inactive:        23552 kB
#HighTotal:      450496 kB
#HighFree:       413788 kB
#LowTotal:       897164 kB
#LowFree:        873572 kB
#SwapTotal:           0 kB
#SwapFree:            0 kB
#Dirty:              52 kB
#Writeback:           0 kB
#AnonPages:        4884 kB
#Mapped:           5464 kB
#Slab:            10836 kB
#SReclaimable:     6216 kB
#SUnreclaim:       4620 kB
#PageTables:        376 kB
#NFS_Unstable:        0 kB
#Bounce:              0 kB
#WritebackTmp:        0 kB
#CommitLimit:    673828 kB
#Committed_AS:    13856 kB
#VmallocTotal:   114680 kB
#VmallocUsed:      5744 kB
#VmallocChunk:   108568 kB
#DirectMap4k:      8192 kB
#DirectMap4M:    909312 kB
def getCpuMem():
    
    meminfo = {}
    
    cmdLine = "cat /proc/meminfo"
    #print "cmdLine = " + cmdLine 
             
    try:
        pipe = os.popen(cmdLine,'r')
        raw = pipe.read().rstrip("\n")
        #print raw
        raw=raw.replace("\n",":")
        
        #print " "
        #print raw
        
        start = raw.find("MemTotal")
        meminfo['memtotal'] = raw[start:].split(':')[1].lstrip(" ")
        
        start = raw.find("MemFree")
        meminfo['memfree'] = raw[start:].split(':')[1].lstrip(" ")
                
        return meminfo

    except Exception,e:                                    
        syslog.syslog("Exception " + `e` + " in getCpuMem(), raw=" + raw);
        return None


########           
# MAIN #           
########           

if __name__ == '__main__':
    print "\nTest 1"
    cpuinfo = getCpuInfo()
    if cpuinfo != None:
        #print "results"
        print cpuinfo

    print "\nTest 2"
    meminfo = getCpuMem()
    if meminfo != None:
        #print "results"
        print meminfo
                                                           