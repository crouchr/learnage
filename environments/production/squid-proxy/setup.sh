#!/usr/bin/env bash
# Bring up the squid server
# This script assumes a CentOS host
# Files on the Host can be accessed via the /vagrant share

set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning squid node"

# Check for patch updates - slows up boot so need a way of avoiding this
yum update -y --disableplugin=fastestmirror

yum install -y wireshark joe
yum install -y squid

# Copy the squid config file
cp /vagrant/squid/squid.conf /etc/squid/squid.conf

echo "Starting squid..."
systemctl enable squid.service
systemctl start squid.service

echo "Finished setup.sh OK for provisioning this squid node"
echo
