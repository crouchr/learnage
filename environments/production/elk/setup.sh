#!/usr/bin/env bash
# https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-elasticsearch-on-centos-7

set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning this node"

yum -y update
yum -y install java-1.8.0-openjdk.x86_64
# cp /vagrant/config.yml /etc/docker-distribution/registry/config.yml

# ELK
wget wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.9.2-x86_64.rpm
rpm -ivh elasticsearch-7.9.2-x86_64.rpm
#yum -y localinstall elasticsearch-7.9.2-x86_64.rpm

# Telegraf
#wget https://dl.influxdata.com/telegraf/releases/telegraf-1.8.3-1.x86_64.rpm
#yum -y localinstall telegraf-1.8.3-1.x86_64.rpm
#cp /vagrant/telegraf.conf /etc/telegraf/telegraf.conf

#echo "Starting Elasticsearch..."
#sudo systemctl enable elasticsearch.service

#echo "Starting Telegraf Agent..."
#systemctl enable telegraf
#systemctl start telegraf

#echo "Starting Docker Registry..."
#systemctl start docker-distribution
#systemctl enable docker-distribution

echo "Finished setup.sh OK for provisioning this node"
echo
