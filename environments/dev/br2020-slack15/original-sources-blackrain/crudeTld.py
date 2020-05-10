#!/usr/bin/python
# Crude code to extract TLD from a hostname since none of the proper libararies work on python 2.5

def getTLD(hostname) :
    tld = "NO_INFO"
    
    if "." not in hostname :
        return "NO_INFO"
    
    print "-----------------"
    fields = hostname.split('.')    
    numFields = len(fields)
    print "hostname=" + hostname
    print fields
    print numFields
    print fields[-1]
    
    
    
    if numFields == 2 :
        tld = hostname
    
    # .co.uk
    if numFields >= 3 and fields[-2] == "co" :
        tld = fields[-3] + "." + fields[-2] + "." + fields[-1]
    elif numFields >= 3 :
        tld = fields[-2] + "." + fields[-1]
    
    return tld
    

if __name__ == '__main__' :
    for hostname in ['mail','mail.vodafone.com.tr','mail.vodafone.com','vodafone.com','mail.vodafone.co.uk','test.mail.vodafone.co.uk','vodafone.nl','test.vodafone.nl','vodafone.co.uk'] :
        tld = getTLD(hostname)
        print hostname + " => " + tld.__str__()