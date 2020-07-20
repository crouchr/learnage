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

yum install -y httpd httpd-devel mod_ssl python-pip
yum install -y dnsmasq bind-utils

# Install PIP
#pip install --upgrade pip
#pip install wheel

#mkdir -p /var/www/html/uploads
#chown -R apache:apache /var/www/html/uploads
# Allow members of apache group (e.g. jenkins user) to upload to this directory
#chmod 775 /var/www/html/uploads

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

echo "Copying 'bad/malware..."
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
