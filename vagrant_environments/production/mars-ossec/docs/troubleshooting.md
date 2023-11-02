# Troubleshooting

## agent to server

- ping from agent to server - it shold be possible

https://trunc.org/ossec/ossec-troubleshooting-agent-to-server-connection-issues
Sniff on the ossec server to see if incoming traffic from the agents (UDP 1514)
[root@mars-ossec ossec]# tcpdump -i eth0 port 1514
