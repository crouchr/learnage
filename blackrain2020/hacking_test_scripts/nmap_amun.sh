# Display vulnerabilities emulated by AMUN
nmap -p 445 -v --open --script smb-vuln* 192.168.1.167
