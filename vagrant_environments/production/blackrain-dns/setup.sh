#!/usr/bin/env bash
# BIND9

set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning this node"

yum update -y --disableplugin=fastestmirror

yum -y install bind bind-utils
systemctl start named
systemctl enable named
systemctl status named

echo 'Copy BIND configuration files...'
cp /vagrant/config/named.conf /etc/
#cp /vagrant/config/ermin.lan.db /var/named/
#cp /vagrant/config/192.168.1.db /var/named/

echo 'Copy BIND check scripts...'
chmod +x /vagrant/scripts/bind_checks.sh
cp /vagrant/scripts/bind_checks.sh /home/vagrant/

# Telegraf
#wget https://dl.influxdata.com/telegraf/releases/telegraf-1.8.3-1.x86_64.rpm
#yum -y localinstall telegraf-1.8.3-1.x86_64.rpm
#cp /vagrant/telegraf.conf /etc/telegraf/telegraf.conf

echo "Enable DNS services..."
sudo systemctl start named
sudo systemctl enable named
sudo systemctl status named

echo "Finished setup.sh OK for provisioning this node"
echo
