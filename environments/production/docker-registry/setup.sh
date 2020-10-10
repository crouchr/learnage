#!/usr/bin/env bash
# https://computingforgeeks.com/install-and-configure-docker-registry-on-centos-7/
# This script is running on the VM itself
# Files on the Host can be accessed via the /vagrant share
# https://www.centlinux.com/2019/04/configure-secure-registry-docker-distribution-centos-7.html
# https://www.petersplanet.nl/index.php/2018/11/18/basic-installation-of-grafana-influxdb-and-telegraf-on-centos-7/

set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning this node"

#yum -y update
yum -y install docker-distribution
cp /vagrant/config.yml /etc/docker-distribution/registry/config.yml

# Telegraf
wget https://dl.influxdata.com/telegraf/releases/telegraf-1.8.3-1.x86_64.rpm
yum -y localinstall telegraf-1.8.3-1.x86_64.rpm
cp /vagrant/telegraf.conf /etc/telegraf/telegraf.conf

#echo "Starting Telegraf Agent..."
#systemctl enable telegraf
#systemctl start telegraf

echo "Starting Docker Registry..."
systemctl start docker-distribution
systemctl enable docker-distribution

echo "Finished setup.sh OK for provisioning this node"
echo
