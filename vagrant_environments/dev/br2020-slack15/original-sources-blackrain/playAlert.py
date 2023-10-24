#!/usr/bin/python
import os
import syslog
import time

# add a time wrapper around this
# play a;ert if during daytime but not nighttime

def playAlert(level):

    # if between 0800 and 2000 then quieten the alarm    
    now=time.time()
    tuple = time.localtime(now)
    hour = tuple.tm_hour
    #print hour
    
    if (int(hour) <= 8 or int(hour) >= 20) :
        volume = 45	# quiet mode
    else :
        volume = 100	# full volume 
            
    if level == 1 :	# haxxor is performing DDoS or serious exploit
        playSound('/home/crouchr/sounds/intruder-alarm.mp3',volume)
    elif level == 2 :	# haxxor has exectud code i.e. "./" or modified honeypot "rm "
        playSound('/home/crouchr/sounds/intruder-alarm.mp3',volume)	
    elif level == 3 :	# haxxor has retrieved toolkit i.e. wget
        playSound('/home/crouchr/sounds/intruder-alarm.mp3',volume)	
    elif level == 4 :	# haxxor has logged in as root or escalated to root
        playSound('/home/crouchr/sounds/intruder-alarm.mp3',volume)	
    elif level == 5 :	# haxxor has logged in non-root
        playSound('/home/crouchr/sounds/intruder-alarm.mp3',volume)	
    else:
        pass

def playSound(filename,volume):
    cmd = 'mpg123 -q -g ' + `volume` + " " + filename + " &"
    print cmd
    syslog.syslog('playSound() : ' + cmd)
    os.system(cmd)
    return

if __name__ == '__main__' : 
    playAlert(3)
    