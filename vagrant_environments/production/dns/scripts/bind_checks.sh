# Run checks on BIND configuration
# TODO : make these BATS tests

sudo named-checkconf /etc/named.conf
sudo named-checkzone ermin.lan /var/named/ermin.lan.db
sudo named-checkzone 1.168.192.in-addr.arpa /var/named/192.168.1.db

nslookup web.ermin.lan 192.168.1.2
nslookup chef.ermin.lan 127.0.0.1
nslookup blackrain-sensor-1.ermin.lan 127.0.0.1
nslookup grafana.ermin.lan 127.0.0.1

# Who is Name Server
dig +short @127.0.0.1 NS ermin.lan

# Test forward lookup:
dig web.ermin.lan +short @127.0.0.1
dig chef.ermin.lan +short @127.0.0.1
dig grafana.ermin.lan +short @127.0.0.1

# Test reverse lookup:
dig -x 192.168.1.102 +short @127.0.0.1
dig -x 192.168.1.71 +short @127.0.0.1
dig -x 192.168.1.1 +short @127.0.0.1