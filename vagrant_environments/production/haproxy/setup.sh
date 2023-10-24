#!/usr/bin/env bash
#

set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning this node"

yum update -y --disableplugin=fastestmirror
yum -y install joe haproxy

echo 'Copy configuration files...'
cp /vagrant/config/haproxy.cfg /etc/haproxy/

# Telegraf
#wget https://dl.influxdata.com/telegraf/releases/telegraf-1.8.3-1.x86_64.rpm
#yum -y localinstall telegraf-1.8.3-1.x86_64.rpm
#cp /vagrant/telegraf.conf /etc/telegraf/telegraf.conf

echo "Enable HAProxy services..."
sudo systemctl enable haproxy

echo "Start HAProxy services..."
sudo systemctl start haproxy

echo "Finished setup.sh OK for provisioning this node"
echo
