#!/usr/bin/python
import os.path

#os.path.isfile
files = ['/home/var/log/blackrain_amun.pcap','/home/var/log/blackrain_honeyd.pcap']


def gatherNonZeroFiles(filelist):
    realFiles = []
    for i in filelist:
        print i
        if os.path.isfile(i) == True:
            if os.path.getsize(i) > 128 :
                realFiles.append(i)
    
    return realFiles    
        


if __name__ == '__main__' :
    files = ['arse.doc','/home/var/log/blackrain_amun.pcap','/home/var/log/blackrain_honeyd.pcap']
    a = gatherNonZeroFiles(files)
    print a     
 




 