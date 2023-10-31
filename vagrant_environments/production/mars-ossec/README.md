mars-ossec server
-----------------
This is the OSSEC server used for receiving mars honeypot logs.  
Main objective is to work on the blackrain-specific rules etc and to use this to 
optimise various log formats for easy parsing by OSSEC

This Vagrant machine will be used to create a pet via OVA export as the installation is not easily 
able to be automated in this version.

For the blackrain-ossec version, that will need to be an automated installation if possible

In the end I could only get 2.8.3 working with the mars 2.8.3 agent

MySQL server is also installed on this node and Ossec writes to it



GeoIP in alerts
---------------
- works on 2.8.3
- see https://marc.info/?l=ossec-list&m=134884291020150

** Alert 1698450510.136507: - ids,
2023 Oct 27 23:48:30 (mars) 192.168.1.67->/home/var/log/attacker-snort.log
Rule: 20101 (level 6) -> 'IDS event.'
Src IP: 219.218.130.151
Src Location: CN,N/A,N/A
Dst IP: 192.168.1.67
Dst Location: RFC1918 IP
Oct 28 00:48:28 mars snort[1234]: [1:2234567:1] IPLOG Port scan [Classification: IPLOG-PSCAN] [Priority: 3]: {TCP} 219.218.130.151:111 -> 192.168.1.67:111


