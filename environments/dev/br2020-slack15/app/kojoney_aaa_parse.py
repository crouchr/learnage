#!/usr/bin/python

import syslog

# add exception handling to this function
def aaaTwittify(tweet):
    
                                                                                                                                                                                                                                       
    tweet = tweet.replace(" rtr_ip=192.168.1.9 " ,  " ")      
    #tweet = tweet.replace("172.29.0.9" ,  "RTR"  )      
    tweet = tweet.replace("crouchr"      , "***"  )              
    
    tweet = tweet.replace("rancid"       , "***"  )	# fixme : do not tweet if username is rancid AND password is funkadelixx               
    tweet = tweet.replace("funkadelixxx" , "***"  )              
    
    tweet = tweet.replace("user_ip" ,  "srcip"  )              
    tweet = tweet.replace(" <cr>" ,  ""  )              
    
    #tweet = tweet.replace("192.168.1.66 " ,  "AMN->"  )             # Medium-interaction  Linux   honeypot
    #tweet = tweet.replace("192.168.1.65 " ,  "NEP->"  )             # Medium-interaction  Win32   honeypot
    #tweet = tweet.replace("192.168.1.64 " ,  "KIP->"  )             # Medium-interaction  SSH     honeypot
    #tweet = tweet.replace("192.168.1.63 " ,  "HYD->"  )             # Low-interaction     generic honeypot
                                                                
    return tweet                                                                                                                                                                                                                                         
                                                                                                                                                                                 
#Fri Jan 28 07:13:50 2011        honeyrtr        cisco   tty0    async   start   task_id=90      start_time=1296198830   timezone=BST    service=shell
#Fri Jan 28 07:14:11 2011        honeyrtr        cisco   tty4    192.168.1.92    start   task_id=91      start_time=1296198851   timezone=BST    service=shell
#Fri Jan 28 07:17:00 2011        honeyrtr        cisco   tty4    192.168.1.92    stop    task_id=92      start_time=1296199019   timezone=BST    service=shell   priv-lvl=1     cmd=show ip cef <cr>
#Fri Jan 28 07:17:13 2011        honeyrtr        cisco   tty4    192.168.1.92    stop    task_id=93      start_time=1296199033   timezone=BST    service=shell   priv-lvl=1     cmd=telnet 192.168.1.131 <cr>
#Fri Jan 28 07:17:23 2011        honeyrtr        cisco   tty4    192.168.1.92    stop    task_id=94      start_time=1296199042   timezone=BST    service=shell   priv-lvl=15    cmd=write memory <cr>
#Fri Jan 28 07:38:34 2011        honeyrtr        root    tty2    192.168.1.92    stop    task_id=51      timezone=BST    service=shell   disc-cause=4    disc-cause-ext=1021    elapsed_time=3655       nas-rx-speed=0  nas-tx-speed=0
#Fri Jan 28 07:47:34 2011        honeyrtr        root    tty3    192.168.1.92    stop    task_id=63      start_time=1296196947   timezone=BST    service=shell   disc-cause=4   disc-cause-ext=1021     elapsed_time=3908       nas-rx-speed=0  nas-tx-speed=0
#Fri Jan 28 07:51:05 2011        honeyrtr        cisco   tty0    async   stop    task_id=107     start_time=1296201065   timezone=UTC    service=shell   priv-lvl=1    cmd=connect DO <cr>
#Fri Jan 28 08:51:41 2011        honeyrtr        cisco   tty0    async   stop    task_id=90      start_time=1296198830   timezone=BST    service=shell   disc-cause=4  disc-cause-ext=1021      elapsed_time=5871       nas-rx-speed=0  nas-tx-speed=0
#Sat Jan 29 04:38:03 2011        honeyrtr        unknown unknown unknown start   task_id=1       timezone=UTC    service=system  event=sys_acct  reason=reload

# tac_plus format Accounting record
def processAcct(line):
  
    try:
       
        line = line.rstrip("\n")
        
        print line
        if line.find("service=shell") == -1 :		# exit if this is not honeyrtr
            return
        if line.find("async") != -1 :			# do not log for console port
            return
        if line.find("cmd=") == -1 :			# do not log 
            return
            
        fields = line.split()
        print fields
        
        tweet = "RTR_ACCT," + fields[6] + " " + fields[7] + " ip=" + fields[8] +  " " + ' '.join(fields[15:])                                                                                                                                             
        tweet = aaaTwittify(tweet)
        return tweet
        
    except Exception,e:
        syslog.syslog("kojoney_aaa_parse.py : processAcct() : " + `e` + " line=" + line)
                                                                                                                                                 

# tac_plus format Authentication
def processAuth(line):
  
    try:
       
        line = line.rstrip("\n")
        #print line
        
        if line.find("async") != -1 :			# do not log for console port
            return
        
        if line.find("rtr_ip=192.168.1.9 ") != -1 :
            fields = line.split()
            #print fields
        
            tweet = "RTR_AUTH," + ' '.join(fields[5:])                                                                                                                                             
            tweet = aaaTwittify(tweet)
            return tweet
        elif line.find("Login aborted") != -1 :
            fields = line.split()
            print fields
            tweet = "RTR_AUTH," + ' '.join(fields[6:])	# the IP is th erouter IP not the attacker IP                                                                                                                                             
            tweet = aaaTwittify(tweet)
            return tweet
        else :
            syslog.syslog("kojoney_aaa_parse.py : processAuth() : unreachable code for line=" + line)
            return None    
        
    except Exception,e:
        syslog.syslog("kojoney_aaa_parse.py : processAuth() : " + `e` + " line=" + line)
                

if __name__ == '__main__' :
    
    # authentication
    filename = '/home/var/log/tacacs.syslog'
    # accounting
    filename = '/home/var/log/tacacs.log'
    
    file = open(filename,'r')
                
    while True:
        line  = file.readline() 
        #tweet = processAuth(line)
        tweet = processAcct(line)
        
        if tweet != None:
            print "tweet:" + tweet
        
