#!/usr/bin/python
import os.path
import syslog

syslog.openlog("checkFilesExist",syslog.LOG_PID,syslog.LOG_LOCAL2)

def gatherNonZeroFiles(filelist,minfilesize):
    realFiles = []
    missingFiles = []
    
    for i in filelist:
        #print i
        if os.path.isfile(i) == True:
            if os.path.getsize(i) > minfilesize :
                realFiles.append(i)
        else:
            missingFiles.append(i)
            
    # Generate a syslog with a list of missing files
    if len(missingFiles) != 0 :
        msg = "checkFilesExist.py : gatherNonZeroFiles() : warning : missing files = " + ' '.join(missingFiles)
        print msg
        syslog.syslog(msg)
            
    return realFiles    
        


if __name__ == '__main__' :
    files = ['notexist.doc','/home/var/log/blackrain_amun.pcap','/nosuchthing.doc','/home/var/log/blackrain_honeyd.pcap']
    a = gatherNonZeroFiles(files,256)
    print a     
 




 