# TODO
- add WUI 
- add MySQl database on the node and write ossec data to it
- add self-signed SSL certs 
- add modsec to protect WUI ?
- add Chef Server on here to make it the 'blackrain management server' ?
- output alerts in JSON format - need 2.9 or above - not possible
- modify mars code to get tsom info to ossec - remove spurious fields before timestamp
- can PSAD be run on mars - there are ossec rules for it
- rename as blackrain-ossec if can get 3.x running
- see if can get running ossec+ very latest code and still works with mars (legacy)
- export as OVA and run on 32GB node as a pet


# role
- Runs correlation of rules (OSSEC)
- Run as Chef Server (or CINQ?) for maintaining hpot agents (config management)
- Stores captured malware 
- Run ClamAV (malware analysis)
- Submits to Cuckoo (malware analysis)
- Sends alerts to upstream ELK system (SIEM)
- Stores raw logs (syslog server)

## Rules

