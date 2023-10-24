#!/usr/bin/env bash
# Bring up the 'RBN' server - simulate a C&C / malware serving host etc'
# This script is running on the VM itself
# Files on the Host can be accessed via the /vagrant share
# DNS info : https://www.tecmint.com/setup-a-dns-dhcp-server-using-dnsmasq-on-centos-rhel/

set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning this node"

# Check for patch updates - slows up boot so need a way of avoiding this
#yum update -y --disableplugin=fastestmirror
#systemctl restart sshd

yum install -y httpd httpd-devel mod_ssl tcpdump
yum install -y dnsmasq bind-utils telnet nmap

echo "Update routing..."
cp /vagrant/files/rc.local /etc/rc.local
chmod +x /etc/rc.d/rc.local

# Inject the routing as rc.local will already have run
ip route add 192.168.10.0/24 via 192.168.1.7

# Copy DNSMASQ files
echo "Copying dnsmasq configuration files..."
cp /vagrant/dnsmasq/dnsmasq.conf /etc/dnsmasq.conf
cp /vagrant/dnsmasq/hosts /etc/hosts

# Make immutable - so that NetworkManager can't override setting
chattr -i /etc/resolv.conf
cp /vagrant/dnsmasq/resolv.conf /etc/resolv.conf
chattr +i /etc/resolv.conf

mkdir -p /var/www/html/badness
chown -R apache:apache /var/www/html/badness

echo "Copying core (root-owned) web server configuration and content..."
cp /vagrant/apache/minimal-index.html /var/www/html/index.html
chown apache:apache /var/www/html/index.html
chmod 755 /var/www/html/index.html
cp /vagrant/apache/minimal-httpd.conf /etc/httpd/httpd.conf

echo "Copying bad/malware..."
cp /vagrant/apache/badness/* /var/www/html/badness/
chmod 755 /var/www/html/badness/*


echo "Starting dnsmasq..."
systemctl enable dnsmasq.service
systemctl start dnsmasq.service

echo "Starting httpd..."
systemctl enable httpd.service
systemctl start httpd.service

echo "Finished setup.sh OK for provisioning this node"
echo
