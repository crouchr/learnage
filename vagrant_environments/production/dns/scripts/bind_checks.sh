# Run checks on BIND configuration
sudo named-checkconf /etc/named.conf
sudo named-checkzone ermin.lan /var/named/ermin.lan.db
sudo named-checkzone 1.168.192.in-addr.arpa /var/named/192.168.1.db

# Test forward lookup:
dig web.ermin.lan +short

# Test reverse lookup:
dig -x 192.168.1.102 +short
