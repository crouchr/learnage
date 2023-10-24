#!/usr/bin/python
#
# soclscrapr : Social (Media) Scraper
#
# taken from : http://andrewbrobinson.com/2011/07/15/using-tweepy-to-access-the-twitter-stream/
# all return values from tweepy status api object -> http://klenwell.com/is/TwitterApiTweepy
# http://badhessian.org/2012/10/collecting-real-time-twitter-data-with-the-streaming-api/

import tweepy
import time
import sys,os
import syslog
import re
import fileinput
import kojoney_alert_client
import ipintellib
import PreludeEasy
import kojoney_idmef_common

# honeytweeter
# ------------
CONSUMER_KEY    = 'N4EpgHKzFe5tf6mqmYqJQ'
CONSUMER_SECRET = 'Vr7Mxg6GdwY70a4w29ClKCqaD5w4BI7gqWPd0G1ME'
ACCESS_KEY      = '19196850-M2WmOBV1voMyFixfBaIJtJ5ol2ntihTte1lCxxRda'
ACCESS_SECRET   = '9kWZw7JYrtNcCGpwhYb2qIsGgSqG88cCCUjjcYMwoE'

VERSION = "1.0"

auth1 = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth1.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api=tweepy.API(auth1)

# Words that mean that Tweet should be ignored
ignoreWords = ['@loic']
ignoreWords = ignoreWords + ['nigga','nigger','shit','fuck','cunt','gay','anal','wank','wanker']

langWhite = ['EN','DE','ES','PT','RO','AL','IT','NL','GR','TR','HU']

# Generate keyword group name                  
def getGroup(keyword):
    try:
        global SEARCHMAP
        for i in SEARCHMAP :
            keywords = SEARCHMAP[i]
            if keyword in keywords :
                #print "**** keyword " + keyword + " found in Group=" + i
                return i
        
        # no match found        
        #print "No match found for keyword=" + keyword
        return "DEFAULT"
                
    except Exception, e:
        msg = "twitter_streamer.py : getGroup() : exception : " + e.__str__() + " : " + group.__str__()
        print msg
        syslog.syslog(msg)

# curl -l TCO =>
#HTTP/1.1 301 Moved Permanently
#cache-control: private,max-age=300
#date: Mon, 29 Apr 2013 06:08:51 GMT
#expires: Mon, 29 Apr 2013 06:13:51 GMT
#location: http://vimeo.com/65031427
#server: tfe
#Content-Length: 0
# These can also resolve to goo.gl and owly !!! - need recursion...
def getRealURLtco(tco):
    try: 
        cmd = "curl -s -i " + tco	# -s = silent -i = include HTTP header
        pipe = os.popen(cmd,'r')
        raw = pipe.read()
        #print raw
        if "location" in raw:
            a = raw.split("\n")
            for line in a :
                if "location" in line:
                    url = line.split("location: ")[1]
                    #print "getRealURLtco(" + tco + ") => " + url
                    return url
        return None              
    except Exception, e:
        msg = "getRealURLtco() : exception : " + e.__str__() + " : " + tco.__str__()
        print msg
        syslog.syslog(msg)
        return None  

#http://t.co/5SKkCtYfvj
# / 
# ips = re.findall("\d+\.\d+\.\d+\.\d+",normalisedTweet)
        
def stripTCO(tweet):
    try:
        a = re.findall("http:\/\/t\.co\/([a-zA-Z0-9]+)",tweet)
        if len(a) > 0 :
            for i in a :
                tco = "http://t.co/" + a[0]
                #print "*** Located Twitter TCO shortening " + tco + " in " + tweet
                #getRealURLtco(tco)
                tweet = tweet.replace(tco," ")
                #print "*** Replaced Twitter TCO shortening " + tco + " new Tweet : [" + tweet + "]"
            return tweet,tco
        else:	# No TCO found
            return tweet,None
                     
    except Exception, e:
        msg = "twitter_streamer.py : stripTCO() : exception : " + e.__str__() + " : " + tweet.__str__()
        print msg
        syslog.syslog(msg)
        return tweet,None
        
# Return normalised Tweet
def logToFile(status):
    try:
         global KEYWORDS
         global SEARCHMAP
         global TweetCache
         
         #print "Entered logToFile()"
                   
         # Ignore Tweet unless it is from a Vodafone country language
         lang = status.author.lang.upper()
         if lang not in langWhite:
             #print "*** langWhite : lang=" + lang + " -> ignore Tweet : " + status.text
             return "NONE","NONE"
         
         if "RT @" in status.text :
             #print "*** Ignoring retweet (RT) : " + status.text
             return "NONE","NONE"
         
         # ignore tweet if is directly to someone
         if status.text[0] == '@':
             #print "*** @ in first position in tweet -> ignore Tweet : " + status.text
             return "NONE","NONE"

         # Ignore Tweet if is contains certain words
         for keyword in ignoreWords:
             if keyword.upper() in status.text.upper():
                 #print "*** IgnoreWord found -> ignore Tweet : " + status.text
                 return "NONE","NONE" 

         # Ignore Tweet unless it is from a Vodafone country language
         for languages in langWhite:
             if keyword in status.text:
                 #print "*** IgnoreWord found -> ignore Tweet : " + status.text
                 return "NONE","NONE"
         
         #print "lang = " + lang.__str__()
         for keyword in KEYWORDS :
             if keyword.upper() in status.text.upper() :
                 text = status.text
                 text = text.replace("\n"," ")
                 text = text.replace("\n"," ")
                 text = text.replace("\n"," ")
                 text = text.replace("\n"," ")
                 text = text.replace("\t"," ")
                 text = text.replace("\t"," ")
                 text = text.replace("\t"," ")
                 text = text.replace("\t"," ")
                 text = text.replace("&gt"," ")
                 
                 #text = text.replace(","," ")
                 text = text.replace('"','')
                 
                 # Get a version of Tweet with ALL instances of TCO shortenings removed 
                 noTCOtweet,tco = stripTCO(text)
                 if tco != None:
                     url = getRealURLtco(tco)
                 else:
                     url = None
                       
                 if TweetCache.update(noTCOtweet) == True :
                     geo    = status.geo 			# nearly always=None       
                     logmsg = status.author.screen_name + "\t" + status.created_at.__str__() + "\t" + status.source + "\t" + text + "\t" + lang.__str__()
                     print "------------------------------------------------------------------------------------------"
                     group = getGroup(keyword)
                     filename = "/home/var/log/" + 'twitterverse_' + group.upper() + '.csv'
                     print time.ctime()
                     print "group  : " + group.upper() + "\n" + "lang   : " + lang + "\n" + "author : " + "@" + status.author.screen_name.encode('utf-8') + "\n" + text
                     print "URL?   : " + url.__str__() 
                     #print "noTCOtweet : " + noTCOtweet.__str__()
                     #print "TCO    : " + tco.__str__()
                     #print "From User " + status.from_user.__str__()
                     
                     fpOut = open(filename,'a')
                     print >> fpOut,logmsg
                     fpOut.close()
                     
                     return group,text
                     
         return "NONE","NONE"            
    
    except Exception, e:
        #return
        #pass
        # need to handle foreign characters
        msg = "logToFile() : exception : " + e.__str__() + " in Tweet [" + status.text + "]"
        #print msg
        #syslog.syslog(msg)
        return "NONE","NONE"


def writeExternalHpotIDMEF(normalisedTweet,status,group,filepath):
    try:
        srcIP = "192.0.2.254"	# just a dummy IP
        dstIP = srcIP
        
        # Create a new Prelude client
        client = PreludeEasy.ClientEasy("blackrain")
        client.Start()      
                                            
        # Create the IDMEF message 
        idmef = PreludeEasy.IDMEF()
                                                                            
        # Sensor
        fieldsSet = kojoney_idmef_common.setIDMEFcommon(idmef,"Twitterverse","02DEBE56",None,None,None,None,None)
                                                                                                                 
        # Classification
        #idmef.Set("alert.classification.text","Interesting Tweet from Twitterverse Stream matched to group " + group.upper())
        idmef.Set("alert.classification.text","Tweet matched " + group.upper() + " via API")
        idmef.Set("alert.assessment.impact.severity", "low")
        idmef.Set("alert.target(0).file(0).path", filepath)
        
        # Assessment
        #idmef.Set("alert.assessment.impact.completion", completion)
        #if completion == "succeeded" :
        #idmef.Set("alert.assessment.impact.description", "File downloaded OK")
        #Belse:
        #idmef.Set("alert.assessment.impact.description", "File download failed")
        
        idmef.Set("alert.source(0).node.address(0).address", srcIP)
        idmef.Set("alert.source(0).service.ip_version", 4)
                     
        idmef.Set("alert.target(0).node.address(0).address", dstIP)
        idmef.Set("alert.target(0).service.ip_version", 4)
                                                                                 
        idmef.Set("alert.assessment.impact.type", "file")
        
        # Additional Data 
        fieldsOffset = fieldsSet
        #print "fieldsOffset = " + fieldsOffset.__str__() 
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "Match group")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", group)                        
        fieldsOffset = fieldsOffset + 1
        
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "Tweeter")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", "@" + status.author.screen_name)                        
        fieldsOffset = fieldsOffset + 1
        
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").type", "string")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").meaning", "Normalised Tweet")
        idmef.Set("alert.additional_data(" + fieldsOffset.__str__() + ").data", normalisedTweet)                        
        fieldsOffset = fieldsOffset + 1
        
        # Send the IDMEF message
        client.SendIDMEF(idmef)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
    except Exception, e:
        msg = "twitter_streamer.py : writeExternalHpotIDMEF() : exception : " + e.__str__() + " : " + normalisedTweet.__str__()
        print msg
        syslog.syslog(msg)
        return
        
# Netmenaces
# ----------
# netmenaces      2013-04-19 02:24:22     toms_honeypot.py        WebApp: GET-based RFI attack from 91.121.79.95 (FR, N/A - N/A) #netmenaces      EN
# netmenaces      2013-04-19 02:33:41     toms_honeypot.py        WebApp: GET-based RFI attack from 65.181.123.47 (US, New Jersey - Rutherford) #netmenaces       EN
# netmenaces      2013-04-19 02:38:00     toms_honeypot.py        A host at 213.178.242.186 (SY, Dimashq - Damascus) tried to log into my honeypot's fake Terminal Services server... #netmenaces EN
# netmenaces      2013-04-19 02:55:36     toms_honeypot.py        A host at 122.226.221.75 (CN, Beijing - Beijing) tried to log into my honeypot's fake MSSQL Server... #netmenaces       EN

# Gyust SSH honeypot
# ------------------
# gyust   2013-04-18 17:29:11     gyust_ssh       His Royal Highness 80.149.218.74 miserably failed after 4 #failure on #SSH connexion attemp ! #ddos     EN
# gyust   2013-04-18 18:01:03     gyust_ssh       His Royal Highness 212.124.107.66 miserably failed after 4 #failure on #SSH connexion attemp ! #ddos    EN
# gyust   2013-04-18 22:56:56     gyust_ssh       His Royal Highness 131.107.5.212 miserably failed after 4 #failure on #SSH connexion attemp ! #ddos     EN
# gyust   2013-04-19 01:06:02     gyust_ssh       His Royal Highness 166.111.230.4 miserably failed after 4 #failure on #SSH connexion attemp ! #ddos     EN
# gyust   2013-04-19 01:39:09     gyust_ssh       His Royal Highness 122.226.34.150 miserably failed after 4 #failure on #SSH connexion attemp ! #ddos    EN

# Use honeytweeter to parse the logs in order to geerate IDMEF
# Only use idmefFlag true for events not covered by kojoney_tweet.py
def writeExternalHpotLogfile(normalisedTweet,status,group,idmefFlag,filepath):            
    try:
        #text = status.text.replace("\n"," ")	# spurious newline in the Tweet
        #text = text.replace("\t"," ")		# spurious TAB     in the Tweet
        text = normalisedTweet
        
        msg = time.ctime() + "," + "@" + status.author.screen_name + "," + text + "," + status.author.lang.upper()
        
        fpOut = open(filepath,"a")
        print >> fpOut,msg
        fpOut.close()
        
        # Send to Prelude SIEM if flag is True
        if idmefFlag == True:
            writeExternalHpotIDMEF(normalisedTweet,status,group,filepath)
        
    except Exception, e:
        msg = "twitter_streamer.py : writeExternalHpotTweetLogfile() : exception : " + e.__str__() + " : " + normalisedTweet.__str__()
        print msg
        syslog.syslog(msg)

def blackListTweet(normalisedTweet,twitterer):
    try:
        twitterer = "@" + twitterer
        ignoreTweetersList = ['@pdonovan92130','@Africanex','@draefon_pi']
        if twitterer in ignoreTweetersList :
            print twitterer + " is in blacklist so do not process"
            return True
        return False    
    except Exception, e:
        msg = "twitter_streamer.py : blackListTweet() : exception : " + e.__str__() + " : " + normalisedTweet.__str__()
        print msg
        syslog.syslog(msg)
        return False
                        
# True = tweet not seen before so cache was updated
class tweetCache:
    
    def __init__(self):
        self.TWEETS = []
        pass
    
    def update(self,tweetText):
        if tweetText not in self.TWEETS :
            if len(self.TWEETS) >= 5000 :
                #print "Flushing Tweets cache..."
                self.TWEETS = []
            self.TWEETS.append(tweetText)
            return True
        #print "**** DUPLICATE tweet so ignore -> " + tweetText    
        return False
                                 
class StreamListener(tweepy.StreamListener):
    #status_wrapper = TextWrapper(width=60, initial_indent='    ', subsequent_indent='    ')
    #conn = mdb.connect('localhost', 'dbUser','dbPass','dbBase')
    def on_status(self, status):
        try:
            #cursor = self.conn.cursor()
            #cursor.execute('INSERT INTO tweets (text, date) VALUES (%s, NOW())' ,(status.text))
            #print self.status_wrapper.fill(status.text)
            #print '\n %s  %s  via %s\n' % (status.author.screen_name, status.created_at, status.source)
            #print status.text
            #print "---------"
            
            #Log to a group file
            #print "on_status() called"
            group,normalisedTweet = logToFile(status)
            if group != "NONE" :
                #print "GROUP = " + group
                flag,event = isInteresting(group,status,normalisedTweet)
                if flag == True :
                    alert(status,group,event,normalisedTweet)
            
        except Exception, e:
        # Catch any unicode errors while printing to console
        # and just ignore them to avoid breaking application.
            print "StreamListener() : exception : " + e.__str__()
            pass

def alert(status,group,subject,normalisedTweet):
    try:
        tweet   = status.text
        subject = "soclscrapr => "  + subject
        body    = "Match Group={" + group + "} Author={" + status.author.screen_name + "} Tweet={" + tweet + "}"
        
        msg     = subject + " : " + body
        
        print " "
        print "++++++++++ ALERT ++++++++++"
        print msg
        print "+++++++++++++++++++++++++++"
        print " "
        
        syslog.syslog("ALERT:" + msg)
        kojoney_alert_client.sendAlert(subject,body,True,True)
         
    except Exception, e:
        msg = "twitter_streamer.py : alert() : exception : " + e.__str__() + " : " + status.text
        print msg
        syslog.syslog(msg)
        
# Also send the alert            
# TODO - determine if destination is in Vodafone IP address space
def checkDoStweet(text,group,victim):
    try:
        global VERSION
        if ("IP" in text.upper() or "TARGET" in text.upper() or "FIRE" in text.upper()) and ("#ANON" in text.upper() or "#OP" in text.upper()):
        
            asInfo = ipintellib.ip2asn(victim)
            asNum = asInfo['as']                                    # AS123 
            asRegisteredCode = asInfo['registeredCode']             # Short-form e.g. ARCOR
                                         
            dnsInfo = ipintellib.ip2name(victim)
            dnsName = dnsInfo['name']
                                          
            geoIP = ipintellib.geo_ip(victim)
            countryCode = geoIP['countryCode'].__str__()
                            
            subject = "Anonymous DDoS Request"
        
            body    = "The text in the Tweet below *MAY* indicate that a hactivist-based DDoS attack is being requested against IP " + victim.__str__() + " DNS=" + dnsName.__str__() \
                    + " located in BGP AS" + asNum.__str__() + " ISP=" + asRegisteredCode.__str__() + " CC=" + countryCode.__str__()
        
            body    = body + " => Tweet="
            body    = body + '[' + text.replace('\t'," ") + ']'
            body    = body + " : "
            body    = body + "This e-mail notification was generated by soclscrpr v" + VERSION + " at " + time.ctime()
            body    = body + " : "
            body    = body + "For support, contact richard.crouch@vodafone.com"
            
            kojoney_alert_client.sendAlert(subject,body,True,True)
        
    except Exception, e:
        msg = "twitter_streamer.py : checkDoStweet() : exception : " + e.__str__() + " : " + text.__str__()
        print msg
        syslog.syslog(msg)
                            
##########################################################################################
# rules
##########################################################################################
def isInteresting(group,status,normalisedTweet):
    try:    
        textUpper = normalisedTweet.upper()
        
        #print "isInteresting() : text=" + text + " group=" + group
        
        # ----- S I G N A T U R E   R U L E S ----- #
        # These are known events so no need to perform Alerting on them once their data is logged for use by BlackRain
        
        # Twitter-enabled honeypot 
        if "SSH CONNEXION ATTEMP" in textUpper:
            writeExternalHpotLogfile(normalisedTweet,status,group,False,"/home/var/log/ext-hpot-gyust.log")
            return False,"NONE"
            
        # Twitter-enabled honeypot    
        if "NETMENACES" in textUpper:
            writeExternalHpotLogfile(normalisedTweet,status,group,False,"/home/var/log/ext-hpot-netmenaces.log")
            return False,"NONE"
        
        # DNS Smurf attack monitor    
        if "IS BEING SMURFED WITH QUERY:" in textUpper:
            writeExternalHpotLogfile(normalisedTweet,status,group,False,"/home/var/log/ext-hpot-dnssmurf.log")
            return False,"NONE"
        
        # Twitter-enabled honeypot
        if " used a " in status.text and "honeypot" and "exploit" and ("smbd" in status.text or "httpd" in status.text or "epmapper" in status.text or "SipSession" in status.text or "mssqld" in status.text): 
            #text = status.text.replace("\n","")	# spurious newline in the Tweet
            writeExternalHpotLogfile(normalisedTweet,status,group,False,"/home/var/log/ext-hpot-evilafoot.log")
            return False,"NONE"
            
        # ----- G E N E R I C  R U L E S ----- #
        
        # Locate IP address in a Tweet - log it so it can be seen if this is another interesting feed
        ips = re.findall("\d+\.\d+\.\d+\.\d+",normalisedTweet)
        if len(ips) > 0 :
            ip = ips[0]
            octets = ip.split(".")
            if int(octets[0]) <= 255 and int(octets[1]) and int(octets[2]) and int(octets[3]) : 
                # Check if this Tweet is not in a list of known boring Tweets
                if blackListTweet(normalisedTweet,status.author.screen_name) == True:
                    return False,"NONE"
                # Check if this Tweet indicates a request to DoS - checkDoStweet() will do it's own alerting
                if checkDoStweet(normalisedTweet,group,ip) == True :
                    return False,"NONE"  
                elif "#MALWAREMUSTDIE" in textUpper or "@MALWAREMUSTDIE" in textUpper:
                    writeExternalHpotLogfile(normalisedTweet,status,group,False,"/home/var/log/ext-hpot-nyxbone.log")
                    return False,"NONE"
                else:    
                    writeExternalHpotLogfile(normalisedTweet,status,group,True,"/home/var/log/ext-ipaddress-generic.log")
                    return False,"NONE"
            
        
        # Uncomment this to generate lots of traffic for testing
        #if group == "vodafone" :
        #    return True,"VODAFONE"
        
        #if group == "hacking" :
        #    return True,"HACKING event"
        
        return False,"NONE"    
    
    except Exception, e:
        msg = "twitter_streamer.py : isInteresting() : exception : " + e.__str__() + " : " + normalisedTweet.__str__()
        print msg
        syslog.syslog(msg)
        return False,"NONE"

##########################################################################################
            
if __name__ == '__main__' :            
    try:
        MAX_API_TERMS = 400	# Maximum number of search terms for Streaming API    
        
        SEARCHMAP = {
        'honeypot_tools'   : ['honeyd','honeynet','nepenthes','maxmind','geoip','kippo','fwsnort','arpwatch','sourcefire','mod security','dionaea','mwcollect','bothunter','ourmon','prelude-ids','ossec','glastopf','glastopf-ng','glastopfng'],
        'honeypots'        : ['beeslikehoney','#netmenaces','honeypot'],
        #'honeytweeter'    : ['#hnytwtr'],
        'pentest'          : ['ethical hacker','opnewblood','ethical hacking','certified ethical hacker','pen test','penetration test'],
         #'hacking'        : ['hacking','hacker','hack'],
        'hacking_tech'     : ['0day','p0wn','phreak','sqli','xss','buffer overflow','phishing','pharming'],
        'dns_attacks'      : ['dns reflection','dns amplification','open resolv','syn flood','out-of-state flood','slow post flood','udp flood','http get flood','slow post flood','slow get flood'],
        'scanners'         : ['metasploit','vulnerability scanner','nessus','nmap','nikto','xprobe','PVS','p0f'],
        'ddos_providers'   : ['prolexic','cloudflare'],
        'ddos_makers'      : ['arbor networks','peakflow','radware','fortinet'],
        'ddos_defence'     : ['RTBH'],
        #'ddos'             : ['ddos','botnet','fireeye','fire-eye','iptables'],
        #'ddos_tools'       : ['anondarthvader','itsoknoproblembro','dorkbot','kaiten','lazor','laz0r',"tor's hammer",'byte dos','r.u.d.y','js-loic','mobile-loic','shell booter','goic','hoic','refref','slowloris','pyloris','nkiller2','brobot','apachekiller'],
        #'apt'              : ['advanced persistent threat','malware','stuxnet','duqu','shamoon'],
        #'cef'              : ['common event format'],
        #'defacement'       : ['deface'],
        #'infosec'          : ['infosec'],
        #'certs'            : ['ASERT','Sans Institute'],
        #'hactivism'        : ['ukuncut'],          
        #'hacker_groups  '  : ['#Identify','@anonops','@AnonNewsDE','titan rain','anonhost','#Anonymous','irc.anonops.com','we are legion','wir sind viele','OpUSA'],
        'secviz'           : ['secviz','graphviz','visualisation','visualization'],
        'siem'             : ['siem','arcsight','idmef','splunk','loggly'],
        'tangodown'        : ['tango down','tangodown'],
        #'cyber'            : ['cybercrime','cyberattack','cyberdefense','cyberdefence','cyberwar'],
        #'cdu'              : ['www.cdu.de','cdu','#opBDA'],
        'vodafone'         : ['vodafone'],
        'logging'          : ['syslog','syslogng','syslog-ng'],
        'vodafone_sites'   : ['vodafone.nl','vodafone.com','vodafone.de','vodafone.es','www.vodafone.ro','www.vodafone.co.uk','www.vodafone.pt'],
        'route_monitor'    : ['bgpmon','routeviews','renesys','packet design'],
        'netflow'          : ['netflow','ipfix','cflow','nprobe','flowspec'],
        'tor'              : ['onion router'],
        'ip'               : ['IP address'],
        #'gov_snooping'     : ['NSA','gchq','room 641a'],
        'ipv6'             : ['IPv6'],
        'bgp_as'           : ['AS3209','AS34419','AS12663'],
        'cisco'            : ['www.cisco.com'],
        'linux'            : ['slackware'],
        'jue_health'       : ['tamoxifen','breast cancer','her2+'],
        #'data_mining'      : ['bluekai','acxiom','datalogix'],
        'other'            : ['natural language toolkit','nltk'],
        }


        #SEARCHMAP = {
        #'test'   : ['hello']
        #}
        
        
        syslog.openlog("soclscrapr")
        
        # Count the number of search terms - Twitter API has a limit (200 ?)
        terms = 0
        for group in SEARCHMAP:
            for i in group :
                terms = terms + 1
        
        msg = "Started => loaded " + len(SEARCHMAP).__str__() + " search groups and " + terms.__str__() + " search terms. MAX_API_TERMS = " + MAX_API_TERMS.__str__()
        print msg
        syslog.syslog(msg)
                
        #print SEARCHMAP.__str__()
        
        ############
        #TEST = True
        TEST = False
        ############
        if TEST == True :
            filename = '/home/var/log/twitterverse_HACKER_GROUPS.csv'
            filename = '/home/var/log/twitterverse_TANGODOWN.csv'
            for line in fileinput.input(filename):
                line = line.rstrip('\n')
                #print line
                #fields = line.split('\t')
                #a = len(fields)
                #print a
                #if a != 3:
                #    continue
                #user  = fields[0]
                #date  = fields[1]
                #text  = fields[2]
                #print user
                #print date
                #print text
                group = "test"
                a = isInteresting(line,group)
                if a == True:
                    print "isInteresting() is True for : " + line.__str__()
                    
            sys.exit("TEST MODE - exiting normally.")
        
        # Normal mode
        # -----------
        print "Connect to Twitter Streaming API..."
        l = StreamListener()
        streamer = tweepy.Stream(auth=auth1, listener=l, timeout=3000000000 )
      
        TweetCache = tweetCache()
        
        # Build list of search terms
        KEYWORDS = []
        for i in SEARCHMAP :
            j = SEARCHMAP[i]
            #print "i=" + i.__str__() + " j=" + j.__str__()
            for k in j:
                KEYWORDS.append(k)
        
        print "KEYWORDS : " + KEYWORDS.__str__()    
        
        print "Listen for data on Twitter Streaming API..."
        streamer.filter(None,KEYWORDS)
    
    except Exception, e:
        print "main() : exception : " + e.__str__()
        
