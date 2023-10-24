#!/usr/bin/python
import sys
import os
import syslog
import glob
#import mailalert
import send_mail

#def statusAlert(subject,content):
#    smtpServer   = 'smtp.btconnect.com'
#    sender       = 'richard_crouch@btconnect.com'
#    #destination  = ['ipbb.mvtc@googlemail.com'] 
#    destination  = ['honeytweeter@gmail.com']    
#    
#    debugLevel   = False
#    debugLevel   = True
#                        
#    try:
#        alertSubject = "BlackRain : " + subject
#        alertContent = content + "\n\nSent by BlackRain\n\n"
#                                    
#        print "alert subject:" + alertSubject + "\nalertContent:\n" + content + "\n"
#                                                                      
#        status = mailalert.mailalert(sender,destination,smtpServer,alertSubject,alertContent,debugLevel)
#                                                                                                  
#        # Add a record to syslog
#        a = "Sent alert e-mail, Subject=" + alertSubject + " to " + destination[0]
#        print a
#        syslog.syslog(a)
#                                                                                                                     
#    except Exception,e:
#        syslog.syslog("analyse_php_scripts.py : statusAlert() : " + e.__str__())


# Convert DOS to UNIX format file
def convert(filenameIn,filenameOut):
    try :
        fp = open(filenameIn,'r')
        text = fp.read()

        text = text.replace('\r','\n')
      
        fpOut = open(filenameOut,'w')
        fpOut.write(text)
        #print "File " + filenameIn + " converted to UNIX format OK"
        return True
        
    except Exception,e:
        msg = "analyse_php_scripts() : convert() : filenameIn = " + filenameIn + " exception = " + e.__str__()         
        print msg
        syslog.syslog(msg)
        return None

# filename = full filename
def makeTweet(filename):
    try :
        botFingerprint = analysePHPfile(filename)
        if botFingerprint == None :
            tweet = None
        else :
            #print "s=Server, p=Port"
            tweet = botFingerprint['filename'] + " type=" + botFingerprint['type'] + " clamAV=" + botFingerprint['clamav'] + " s=" + botFingerprint['server'] + " p=" + botFingerprint['port'] + " ch=" + botFingerprint['channel'] + " fl=" + botFingerprint['flooder']
            #print tweet
        
        # code join
        return tweet
        
    except Exception,e:
        msg = "analyse_php_scripts() : makeTweet() : botFingerprint = " + botFingerprint.__str__() + " exception = " + e.__str__()         
        print msg
        syslog.syslog(msg)
        return None

# param = "chan"
def getArrayVal(line,param):
    try:
        a = line.strip()

        a = a.replace("var $config = array(" , "") 	# first part of array
    
        b = '"' + param + '"' + '=>'
        #print b
        #a = a.replace('"chan"=>',"")
        a = a.replace(b,"")
        a = a.replace(',',"")
        a = a.replace('"',"")
    
        a = a.split("//")[0]	# ditch comments
        a = a.rstrip(" ")		# ditch trailing whitespace
    
        return a
    
    except Exception,e:
        msg = "analyse_php_scripts.py : getArrayVal() : exception " + e.__str__()         
        print msg
        syslog.syslog(msg)
        return None
    

def crack_pBot(filename,fingerprint):
    try:
        #print "*** crack_pBot() : filename = " + filename
        
        fingerprint['type']     = "pBot"
    
        fp = open(filename,'r')
    
        code = fp.read()
        code = code.split("\n")
        
        for line in code:
            #print "crack_pBot() : look for keywords in " + line
            if line.find('"chan"=>') >= 0 :
                fingerprint['channel'] = getArrayVal(line,"chan")
                #print "crack_pBot() : located keyword : channel"
                
            if line.find('"port"=>') >= 0 :
                #print line.lstrip()
                fingerprint['port']  = getArrayVal(line,"port")
                #print "crack_pBot() : located keyword : port"
                
            if line.find('"server"=>') >= 0 :
                #print line.lstrip()
                fingerprint['server']  = getArrayVal(line,"server")
                #print "crack_pBot() : located keyword : server"
                
            if line.find('"prefix"=>') >= 0 :
                #print line.lstrip()
                fingerprint['prefix']  = getArrayVal(line,"prefix")
                #print "crack_pBot() : located keyword : prefix"
                
            if line.find('"pass"=>') >= 0 :
                #print line.lstrip()
                fingerprint['pass']  = getArrayVal(line,"pass")
                #print "crack_pBot() : located keyword : pass"
                
            if line.find('"modes"=>') >= 0 :
                #print line.lstrip()
                fingerprint['modes']  = getArrayVal(line,"modes")
                #print "crack_pBot() : located keyword : modes"
                
            #if line.find('"hostauth"=>') >= 0 :
            #    print line.lstrip()
            #    fingerprint['hostauth']  = getArrayVal(line,"hostauth")
        
        #print "crack_pBot() -> " + fingerprint.__str__()
        
        return fingerprint
    
    except Exception,e:
        msg = "analyse_php_scripts.py : crack_pBot() : exception " + e.__str__()         
        print msg
        syslog.syslog(msg)
        return None
    
# =======================================
    
# Characterise the bot
# fn calling parameter : filename = full pathname
def getBotFingerprint(filetype,clamav,filename) :
    try:
        #print "Entered getBotFingerprint()"
        
        fingerprint = {}
        fingerprint['filename'] = "?"
        fingerprint['type']     = "?"
        fingerprint['size']     = "?"
        fingerprint['server']   = "?"
        fingerprint['port']     = "?"
        fingerprint['channel']  = "?"
        fingerprint['user']     = "?"
        fingerprint['nick']     = "?"
        fingerprint['script']   = "?"
        fingerprint['scanner']  = "?"
        fingerprint['flooder']  = "?"
        fingerprint['clamav']   = "?"
        
        
        fingerprint['filetype'] = filetype
        fingerprint['clamav']   = clamav
        
        fingerprint['size']     = os.path.getsize(filename).__str__()
        fingerprint['filename'] = os.path.basename(filename).__str__()
               
        fp = open(filename,'r')
        text = fp.read()
        #print "text = " + text
        
        if text.find("<?php") >= 0 :
            fingerprint['script'] = "php"
        
        if text.find("base64_decode") >= 0 :    
            fingerprint['type'] = "base64_encoded"
            
        # Put most specific matches at the end of this function to override more generic ones at front    
        
        # Generic signature x 3
        IRC_SIGS = ['join','nick','privmsg']
        for sig in IRC_SIGS:
            if sig in text.lower() :    
                fingerprint['type'] = "IRC"
        
        FLOOD_SIGS = ['udpflood','tcpflood','flood']
        for sig in FLOOD_SIGS:
            if sig in text.lower() :    
                fingerprint['flooder'] = "yes"
        
        SCAN_SIGS = ['scan','.scan']
        for sig in SCAN_SIGS:
            if sig in text.lower() :    
                fingerprint['flooder'] = "yes"
        
        # bot-specific decode : "class pBot"
        if "class pBot" in text :
            #print "getBotFingerprint() : Located pBot signature in " + filename
            fingerprint = crack_pBot(filename,fingerprint)
        #else:
            #print "getBotFingerprint() : signature pBot NOT found in " + filename
                
        #sys.exit("Aborted code during testing")    
        
        #print "GetBotFingerprint() -> " + fingerprint.__str__()
        
        return fingerprint

    except Exception,e:
        msg = "analyse_php_scripts.py : getBotFingerprint() : filename = " + filename + " exception = " + e.__str__()         
        print msg
        syslog.syslog(msg)
        return None
    
# Determine type of file using UNIX file utility
# Need to rename this - it is not only PHP files now
def isPHPfile(filename) :
    try : 
        cmd = "file " + filename
        #print "cmd : " + cmd
        pipe = os.popen(cmd,'r')    
        result = pipe.read().rstrip("\n")
        #print "isPHPfile() : result " + result
        
        if result.find("PHP script") >= 0 :
            return "PHP"
        if result.find("Python script ") >= 0 :
            return "Python"
        if result.find("Perl script ") >= 0 :
            return "Perl" 
        if result.find("data") >= 0 :		# generic file - some PHP bots return this
            return "DATA" 
        if result.find("HTML ") >= 0 :
            return "HTML" 
            
        return "Undetermined"   
    
    except Exception,e:
        msg = "analyse_php_scripts.py : isPHPfile() : filename = " + filename + " exception = " + e.__str__()         
        print msg
        syslog.syslog(msg)
        return None
        
# ========         
        
# Main function to be called from BlackRain        
def analysePHPfile(filename):        
    try :
        print "analysePHPfile() : filename=" + filename.__str__()
        # First thing to do is virus scan the file
        cmd = "clamscan --no-summary " + filename
        #print "analysePHPfile() : cmd=" + cmd.__str__()
        
        #result = "Test code, bypassing ClamAV for speed"
        pipe = os.popen(cmd,'r')    
        result = pipe.read().rstrip("\n")
        print "ClamAV on " + filename + " -> " + result
    
        if "FOUND" in result :
            clamav = result.split(" ")[1]
            #print clamav
        else :
            clamav = "OK"    
        #print "Clamav scan of " + filename + " -> " + clamav
            
        filenameOut = filename + ".php"
        #print "filenameOut constructed to be : " + filenameOut
        filetype = isPHPfile(filename)
        if filetype != None :
            #print " -> filetype = " + filetype.__str__()
            convert(filename,filenameOut)
            botFingerprint = getBotFingerprint(filetype,clamav,filenameOut)
            
            print "analysePHPfile() : Bot fingerprint = " + botFingerprint.__str__()
            
            return botFingerprint    
        else:
            return None
            
    except Exception,e:
        msg = "analyse_php_scripts.py : analysePHPfile() : filename = " + filename + " exception = " + e.__str__()         
        print msg
        syslog.syslog(msg)
                
# ===========================
    
# testing stub    
# run with 
# python analyse_php_scripts.py /usr/local/src/glastopf/files/get     
#
if __name__ == '__main__' :
    
    try :            
        report = ""
        print "analyse_php_scripts.py : Started OK"     
        if len(sys.argv) != 2 :
            directory = "/usr/local/src/glastopf/files/get"	# use a sensible default
            #sys.exit("Need to supply name of directory as a command-line argument, exiting...")
        else:    
            directory = sys.argv[1]
    
        ANALYSE_SUMMARY_REPORT = "/home/crouchr/analyse_php_scripts_summary.txt"
        fpSummary  = open(ANALYSE_SUMMARY_REPORT,'w')
        
        #fpAllFiles = open("analyse_php_scripts_all_files.txt",'w')
        
        print "Start loop, analyse PHP files in : " + directory    
        print "Results summary file (output) : " + ANALYSE_SUMMARY_REPORT
        
        globPattern = "/*"
        #globPattern = "/8088*"			# just do one file - good for testing
        for filenameIn in glob.glob(directory + globPattern) :
            if "archive" in filenameIn:		# ignore this directory
                continue
            print "-----------------------------------------------------------------------------------------"
            print "analysing malware file : " + filenameIn + " ..." 
            
            #******************************************
            botFingerprint = analysePHPfile(filenameIn)
            #******************************************
            
            msg = "Malware file : " + os.path.basename(filenameIn)	# not interested in full path, just the MD5 filename
            msg = msg  + "\n"
            if botFingerprint != None :
                #msg = msg + "," + botFingerprint.__str__()
                for i in botFingerprint :
                    if botFingerprint[i] != '-' and botFingerprint[i] != '?' :
                        msg = msg + " " + i + "=" + botFingerprint[i] + "\n"
            else:
                msg = msg + " " + " -> Unable to detect bot in file"
                botFingerprint = None
                     
            msg = msg + "\n"
            print msg 
            print >> fpSummary,msg
            report = report + msg
              
            msg = "Tweet : " + makeTweet(filenameIn).__str__() + "\n"
            print msg + "\n"
            print >> fpSummary,msg
            report = report + msg
        
            msg = "---------------------------------------------------------------------\n"
            print >> fpSummary,msg
            report = report + msg
            #print "report so far :-" + "\n" + report
        
        fpSummary.close()        
        
        # send as an attachment
        files = []
        files.append(ANALYSE_SUMMARY_REPORT)
        recipients = ['honeytweeter@gmail.com']   
        text = "This e-mail is generated automatically by the BlackRain Honeynet\n"
        send_mail.send_mail('richard_crouch@btconnect.com',recipients,"BlackRain : Malware Scripts Juicer Report" , text, files, 'smtp.btconnect.com')
        
    except Exception,e:
        msg = "analyse_php_scripts.py : main() : exception " + e.__str__()
        print msg
        syslog.syslog(msg)
        