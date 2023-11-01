# TODO
- add WUI 
- add MySQl database on the node and write ossec data to it
- add self-signed SSL certs 
- add modsec to protect WUI ?
- add Chef Server on here to make it the all-in-one 'mars (legacy) management server' ?
- output alerts in JSON format - need 2.9 or above - not possible
- modify mars code to get tsom info to ossec - remove spurious fields before timestamp
- can PSAD be run on mars - there are ossec rules for it
- rename as blackrain-ossec if can get 3.x running
- see if can get running ossec+ very latest code and still works with mars (legacy)
- export as OVA and run on 32GB node as a pet

# long-term
- Can I build it on a Rocky 8 Linux machine before Centos7 runs out -> create a Packer job for Rocky 8

# role
- Runs correlation of rules (OSSEC)
- Run as Chef Server (or CINQ in future) for maintaining hpot agents (config management)
- Stores captured malware 
- Runs as a general MySQL Server
- Run ClamAV (malware analysis)
- Submits to Cuckoo (malware analysis)
- Sends alerts to upstream ELK system (SIEM)
- Stores raw logs (syslog-ng server)
- Produce visualisations using AfterGlow (and email them)
- Send TIMP data to TIM
- Single location for Snort rules. mars downloads them nightly via http
- Add Docker and then run the mars REST container to MQTT adapter
- Run TSOM algorithm centrally (in a Docker container)

## Rules

