#!/usr/bin/env bash
# Bring up the squid server
# This script assumes a CentOS host
# Files on the Host can be accessed via the /vagrant share

set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning Squid v3.5.20 node"

# Check for patch updates - slows up boot so need a way of avoiding this
yum update -y --disableplugin=fastestmirror

yum install -y wireshark joe
yum install -y squid

# Configure node
cp /vagrant/squid/motd /etc/

#cp /vagrant/squid/squid.conf /etc/squid/squid.conf
cp /vagrant/squid/squid-pip-proxy.conf /etc/squid/squid.conf

mkdir -p /etc/squid/certs
cp /vagrant/squid/certs/squid.pem /etc/squid/certs/
chown squid:squid -R /etc/squid/certs
chmod 700 /etc/squid/certs/squid.pem

#echo "Create database..."
#./usr/lib64/squid/ssl_crtd -c -s /var/lib/ssl_db

echo "Starting Squid..."
systemctl enable squid.service
systemctl start squid.service

echo "Create database..."
./usr/lib64/squid/ssl_crtd -c -s /var/lib/ssl_db

echo "Finished setup.sh OK for provisioning this Squid v3.5.20 node"
echo
