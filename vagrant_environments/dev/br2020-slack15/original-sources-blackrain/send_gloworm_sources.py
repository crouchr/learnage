#!/usr/bin/python
# todo : encrypt the source code so only I have it
# add :
# other major source code - p0f, python libraries
# cron.daily shell file
# ntp conf
#
import time, os , syslog  
import send_mail		# RCH library
import checkFilesExist		# RCH library       
import googleMail		# RCH library

# ----------------------------------------------
        
syslog.openlog("send_gloworm_sources")         # Set syslog program name    

syslog.syslog("send_gloworm_sources.py : Started")

# list of files to be e-mailed
files = ['/home/crouchr/kojoney_tail.py',\
'/home/crouchr/getSnortInfo.py',\
'/home/var/secviz/go_graph',\
'/home/var/secviz/honeypot.properties',\
'/home/var/secviz/bgpguard.properties',\
'/home/var/secviz/darknet.properties',\
'/home/var/secviz/drone.properties',\
'/home/var/secviz/nmap.properties',\
'/home/var/secviz/passer.properties',\
'/home/crouchr/send_gloworm_sources.py',\
'/home/crouchr/kojoney_ar.py',\
'/usr/local/src/spamhole/spamhole.h',\
'/usr/local/src/spamhole/spamhole.c',\
'/home/crouchr/kojoney_bitly.py',\
'/home/crouchr/kojoney_viz.py',\
'/home/crouchr/kojoney_sagen.py',\
'/home/crouchr/kojoney_tweet.py',\
'/home/crouchr/kojoney_tweet_engine.py',\
'/home/crouchr/kojoney_statd.py',\
'/home/crouchr/kojoney_defend.py',\
'/home/crouchr/attacker_statd.py',\
'/home/crouchr/blackrain_agent.sh',\
'/home/crouchr/blackrain_agent.py',\
'/home/crouchr/kojoney_guru.py',\
'/home/crouchr/kojoney_analyst.py',\
'/home/crouchr/traceroute_matrix.py',\
'/home/crouchr/kojoney_ultimatenotification.py',\
'/home/crouchr/kojoney_twitter_drone.py',\
'/home/crouchr/kojoney_funcs.py',\
'/home/crouchr/kojoney_amun_parse.py',\
'/home/crouchr/kojoney_amun_idmef.py',\
'/home/crouchr/idmef_test.py',\
'/home/crouchr/analyse_php_scripts.py',\
'/home/crouchr/kojoney_aaa_parse.py',\
'/home/crouchr/kojoney_bro_parse.py',\
'/home/crouchr/kojoney_kippo_parse.py',\
'/home/crouchr/kojoney_spade_parse.py',\
'/home/crouchr/kojoney_telnetd_idmef.py',\
'/home/crouchr/kojoney_anubis.py',\
'/home/crouchr/kojoney_anubis_idmef.py',\
'/home/crouchr/kojoney_telnetd_parse.py',\
'/home/crouchr/kojoney_spamholed_idmef.py',\
'/home/crouchr/kojoney_idmef_common.py',\
'/home/crouchr/kojoney_spamhole_parse.py',\
'/home/crouchr/kojoney_kippo_idmef.py',\
'/home/crouchr/kojoney_blackhole_idmef.py',\
'/home/crouchr/kojoney_glastopf_parse.py',\
'/home/crouchr/kojoney_glastopf_idmef.py',\
'/home/crouchr/kojoney_guru_parse.py',\
'/home/crouchr/kojoney_honeyd_parse.py',\
'/home/crouchr/kojoney_honeytrap_parse.py',\
'/home/crouchr/kojoney_honeytrap_idmef.py',\
'/home/crouchr/kojoney_pads_parse.py',\
'/home/crouchr/kojoney_passer_parse.py',\
'/home/crouchr/kojoney_iplog_parse.py',\
'/home/crouchr/kojoney_iplog_idmef.py',\
'/home/crouchr/kojoney_hiddenip.py',\
'/home/crouchr/passer-v1.16.py',\
'/home/crouchr/kojoney_p0f_parse.py',\
'/home/crouchr/kojoney_argus_parse.py',\
'/home/crouchr/kojoney_argus_idmef.py',\
'/home/crouchr/kojoney_ossec_parse.py',\
'/home/crouchr/kojoney_suricata_parse.py',\
'/home/crouchr/kojoney_router_parse.py',\
'/home/crouchr/kojoney_suricata_syslog.py',\
'/home/crouchr/kojoney_blackrain.py',\
'/home/crouchr/blackrain_netflow.pl',\
'/home/crouchr/blackrain_netflow.py',\
'/home/crouchr/blackrain_dev/blackrain.py',\
'/home/crouchr/blackrain_dev/blackrain_bootstrap.py',\
'/home/crouchr/blackrain_dev/blackrain_super.py',\
'/home/crouchr/blackrain_dev/register.py',\
'/home/crouchr/blackrain_dev/blackrain_stun.py',\
'/home/crouchr/blackrain_dev/blackrain_mac.py',\
'/home/crouchr/ps-monitor.py',\
'/home/crouchr/filter_sebek.py',\
'/home/crouchr/playAlert.py',\
'/home/crouchr/geoip_ips.py',\
'/home/crouchr/tweep.py',\
'/home/crouchr/kojoney_funcs.py',\
'/home/crouchr/ipintellib.py',\
'/home/crouchr/scan_malware.py',\
'/home/crouchr/kill_blackrain.sh',\
'/home/crouchr/checkFilesExist.py',\
'/home/crouchr/twitter_funcs.py',\
'/home/crouchr/sec-testing/kojoney_defcon.conf',\
'/home/crouchr/send_kojoney_logs.py',\
'/home/crouchr/potaroo.py',\
'/home/crouchr/asn_get_routeviews.py',\
'/home/crouchr/bgpguard_ddos.py',\
'/home/crouchr/send_gloworm_sources.py',\
'/home/crouchr/send_blackrain_sources.py',\
'/etc/cron.gloworm/gloworm.sh',\
'/etc/cron.drone/drone.sh',\
'/etc/monitrc',\
'/etc/fwsnort/fwsnort.conf',\
'/etc/fwsnort/snort_rules/go_fwsnort',\
'/etc/fwsnort/snort_rules/unthreshold_snort.py',\
'/etc/fwsnort/snort_rules/unthreshold_rules.sh',\
'/etc/psad/psad.conf',\
'/etc/psad/snort_rule_dl',\
'/etc/psad/auto_dl',\
'/etc/snort/snort.conf',\
'/etc/suricata/suricata.yaml',\
'/etc/suricata/threshold.config',\
'/etc/suricata/classification.config',\
'/etc/syslog.conf',\
'/etc/syslog-ng.conf',\
'/etc/snmpd.conf',\
'/etc/honeyd/honeyd.conf',\
'/etc/honeytrap/honeytrap.conf',\
'/etc/honeyd/honeydstats.conf',\
'/usr/local/src/amun/conf/amun.conf',\
'/usr/local/src/amun/conf/submit-anubis.conf',\
'/usr/local/src/amun/conf/submit-joebox.conf',\
'/usr/local/src/amun/conf/submit-cwsandbox.conf',\
'/etc/rc.d/rc.local',\
'/etc/rc.d/rc.gloworm',\
'/etc/rc.d/rc.honeyd',\
'/etc/rc.d/rc.honeydstats',\
'/etc/rc.d/rc.faketelnetd',\
'/etc/rc.d/rc.spamhole',\
'/etc/rc.d/rc.kojoney_tail',\
'/etc/rc.d/rc.kojoney_ar',\
'/etc/rc.d/rc.kojoney_defend',\
'/etc/rc.d/rc.kojoney_guru',\
'/etc/rc.d/rc.kojoney_analyst',\
'/etc/rc.d/rc.kojoney_tweet_engine',\
'/etc/rc.d/rc.kojoney_statd',\
'/etc/rc.d/rc.kojoney_viz',\
'/etc/rc.d/rc.sebekd',\
'/etc/rc.d/rc.kippo',\
'/etc/rc.d/rc.sec',\
'/etc/rc.d/rc.kojoney_suricata_syslog',\
'/etc/rc.d/rc.suricata',\
'/etc/rc.d/rc.honeyd',\
'/etc/rc.d/rc.snort']

# Generate a list of the files that exist
a = len(files)

filesExist=checkFilesExist.gatherNonZeroFiles(files,1)
b = len(filesExist)
print filesExist

if a != b:
    msg = "Some expected source files could not be found : expected=" + `a` + " actual=" + `b`
    print "\nWARNING : " + msg
    syslog.syslog("send_gloworm_sources.py : " + msg)
    
#recipients =['ipbb.mvtc@googlemail.com']
recipients =['honeytweeter@gmail.com']
text = "This e-mail is generated automatically by the BlackRain Honeynet\n"

#send_mail.send_mail('richard_crouch@btconnect.com',recipients,"BlackRain : Source code" , text, filesExist, 'smtp.btconnect.com')
googleMail.sendViaGmail('uber.koob@gmail.com','fuckfacebook',recipients,"BlackRain : Source code",text,filesExist)

syslog.syslog("send_gloworm_sources.py : Finished, " + `b` + " BlackRain source files backed up to Gmail")
                            