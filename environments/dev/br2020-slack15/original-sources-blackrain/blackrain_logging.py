#!/usr/bin/python
#/usr/local/bin/python

# standard Python libraries
import time,sys
import syslog,logging

def setLogging(mode='a'):
    logging.basicConfig(level=logging.INFO,
        format='%(asctime)s %(filename)s : %(levelname)s > %(message)s',
        datefmt='%m-%d %H:%M:%S',
        filename="/home/br/blackrain.log",
        filemode=mode)
        
#format='%(asctime)s %(name)-6s %(levelname)s: %(message)s',
        
    
if __name__ == '__main__' :
    
    try:
        setLogging(mode='w')
        logging.info("Zeroed logfile")
        #print "Finished"
    
    except Exception, e:
        a = "Exception " + e.__str__() + " in blackrain_logging.py main()"
        print a
        syslog.syslog(a)
