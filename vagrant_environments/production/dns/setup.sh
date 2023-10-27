#!/usr/bin/env bash
set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning this node"

# This needs to go in Packer build
sudo timedatectl set-timezone Europe/London

yum update -y --disableplugin=fastestmirror

yum -y install bind bind-utils
systemctl start named
systemctl enable named
systemctl status named

# FIXME : Do this in Packet job ?
#echo 'Disable SELINUX configuration files...'
#cp /vagrant/config/selinux /etc/sysconfig/selinux
#setenforce 0
#sestatus

echo 'Copy BIND configuration files...'
cp /vagrant/config/named.conf /etc/
cp /vagrant/config/ermin.lan.db /var/named/
cp /vagrant/config/192.168.1.db /var/named/

echo 'Copy BIND check scripts...'
chmod +x /vagrant/scripts/bind_checks.sh
cp /vagrant/scripts/bind_checks.sh /home/vagrant/

# Telegraf
#wget https://dl.influxdata.com/telegraf/releases/telegraf-1.8.3-1.x86_64.rpm
#yum -y localinstall telegraf-1.8.3-1.x86_64.rpm
#cp /vagrant/telegraf.conf /etc/telegraf/telegraf.conf

sudo mkdir -p /var/log/named
touch /var/log/named/normal.log
chmod -R 755 /var/log/named
chown named: /var/log/named/normal.log

sudo mkdir -p /run/named
chown named: "/run/named"

echo "Enable and start BIND (named) services..."
sudo systemctl enable named
sudo systemctl start named
sudo systemctl status named

# Dump the status of the BIND server
sudo rndc status

#echo "Smoke checks"
#nslookup web.ermin.lan 127.0.0.1
#nslookup chef.ermin.lan 127.0.0.1
#nslookup blackrain-sensor-1 127.0.0.1
#nslookup grafana.ermin.lan 127.0.0.1

echo "Finished setup.sh OK for provisioning this node"
echo
