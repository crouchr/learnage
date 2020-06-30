#!/usr/bin/env bash
# This script is running on the VM itself
# Files on the Host can be accessed via the /vagrant share
# https://www.urban-software.com/cacti-howtos/howto-install-influxdb-on-centos/

set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning this node"

# Check for patch updates - slows up boot so need a way of avoiding this
#yum update -y --disableplugin=fastestmirror

# Need accurate time
yum -y install ntp
cho "Starting NTPd..."
systemctl enable ntpd
systemctl start ntpd

# InfluxDB
cat <<EOF | sudo tee /etc/yum.repos.d/influxdb.repo
[influxdb]
name = InfluxDB Repository - RHEL \$releasever
baseurl = https://repos.influxdata.com/rhel/\$releasever/\$basearch/stable
enabled = 1
gpgcheck = 1
gpgkey = https://repos.influxdata.com/influxdb.key
EOF

yum -y install influxdb
mkdir -p /etc/influxdb
cp /vagrant/influxdb.conf /etc/influxdb/influxdb.conf

# Grafana
wget https://s3-us-west-2.amazonaws.com/grafana-releases/release/grafana-5.3.4-1.x86_64.rpm
yum -y localinstall grafana-5.3.4-1.x86_64.rpm
mkdir -p /etc/grafana
cp /vagrant/grafana.ini /etc/grafana/grafana.ini

# Telegraf
wget https://dl.influxdata.com/telegraf/releases/telegraf-1.8.3-1.x86_64.rpm
yum -y localinstall telegraf-1.8.3-1.x86_64.rpm
mkdir -p /etc/telegraf
cp /vagrant/telegraf.conf /etc/telegraf/telegraf.conf

echo "Starting InfluxDB..."
systemctl enable influxdb
systemctl start influxdb

echo "Starting Telegraf..."
systemctl enable telegraf
systemctl start telegraf

echo "Starting Grafana..."
systemctl enable grafana-server
systemctl start grafana-server
#systemctl status grafana-server

echo "Finished setup.sh OK for provisioning this node"
echo
