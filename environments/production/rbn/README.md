Purpose
=======
This server node runs the following services that are exposed to honeypots

- Web-server
- DNSMASQ

Web-server
----------
The 'badness' folder contains malware that can be downloaded on the honeypot to test alerting meechanisms

DNSMASQ
-------
The dnsmasq instance is a DNS proxy that is used by the honeypots as it is set to log all dns queries to syslog.
Jul 20 07:59:46 centos7 dnsmasq[3430]: query[A] www.cisco.com from 192.168.1.99
Jul 20 07:59:46 centos7 dnsmasq[3430]: forwarded www.cisco.com to 8.8.4.4
Jul 20 07:59:46 centos7 dnsmasq[3430]: forwarded www.cisco.com to 8.8.8.8
Jul 20 07:59:46 centos7 dnsmasq[3430]: reply www.cisco.com is <CNAME>
Jul 20 07:59:46 centos7 dnsmasq[3430]: reply www.cisco.com.akadns.net is <CNAME>
Jul 20 07:59:46 centos7 dnsmasq[3430]: reply wwwds.cisco.com.edgekey.net is <CNAME>
Jul 20 07:59:46 centos7 dnsmasq[3430]: reply wwwds.cisco.com.edgekey.net.globalredir.akadns.net is <CNAME>
Jul 20 07:59:46 centos7 dnsmasq[3430]: reply e2867.dsca.akamaiedge.net is 104.82.199.178
Jul 20 07:59:52 centos7 chronyd[592]: Selected source 80.127.119.186
