# run with sudo
iptables -A INPUT -i enp0s03 -p tcp --syn -m state --state NEW -j QUEUE
