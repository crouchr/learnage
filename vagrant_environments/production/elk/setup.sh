#!/usr/bin/env bash
# https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-elasticsearch-on-centos-7

set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning this ELK 7.9.2 (OSS) node"

yum update -y --disableplugin=fastestmirror

echo 'Installing Java 11 JDK...'
# yum -y install java-1.8.0-openjdk.x86_64
yum -y install java-11-openjdk-devel

# cp /vagrant/config.yml /etc/docker-distribution/registry/config.yml

mkdir -p /etc/elasticsearch
mkdir -p /etc/logstash/conf.d
mkdir -p /etc/kibana

# ELK
#wget -O /tmp/elasticsearch-7.9.2-x86_64.rpm https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.9.2-x86_64.rpm
#rpm -ivh /tmp/elasticsearch-7.9.2-x86_64.rpm
#yum -y localinstall elasticsearch-7.9.2-x86_64.rpm

wget -O /tmp/elasticsearch-oss-7.9.2-x86_64.rpm http://192.168.1.4/centos7-packages/elasticsearch-oss-7.9.2-x86_64.rpm
wget -O /tmp/logstash-oss-7.9.2.rpm http://192.168.1.4/centos7-packages/logstash-oss-7.9.2.rpm
wget -O /tmp/kibana-oss-7.9.2-x86_64.rpm http://192.168.1.4/centos7-packages/kibana-oss-7.9.2-x86_64.rpm

echo 'Copy packages...'
#cp /vagrant/packages/*.rpm /tmp/
yum -y localinstall /tmp/elasticsearch-oss-7.9.2-x86_64.rpm
yum -y localinstall /tmp/logstash-oss-7.9.2.rpm
yum -y localinstall /tmp/kibana-oss-7.9.2-x86_64.rpm

# rpm -ivh /tmp/elasticsearch-oss-7.9.2-x86_64.rpm
# rpm -ivh /tmp/kibana-oss-7.9.2-x86_64.rpm

echo 'Copy configuration files...'
cp /vagrant/config/ip_to_honeypot_name_mapping.csv /tmp/
cp /vagrant/config/elasticsearch.yml /etc/elasticsearch/elasticsearch.yml
cp /vagrant/config/logstash.conf /etc/logstash/conf.d/logstash.conf
cp /vagrant/config/kibana.yml /etc/kibana/kibana.yml

# Telegraf
#wget https://dl.influxdata.com/telegraf/releases/telegraf-1.8.3-1.x86_64.rpm
#yum -y localinstall telegraf-1.8.3-1.x86_64.rpm
#cp /vagrant/telegraf.conf /etc/telegraf/telegraf.conf

echo "Enable ELK services..."
systemctl daemon-reload
systemctl enable elasticsearch.service
systemctl enable logstash.service
systemctl enable kibana.service

echo "Start ELK services..."
sudo systemctl start elasticsearch.service
sudo systemctl start logstash.service
sudo systemctl start kibana.service

echo "Finished setup.sh OK for provisioning this ELK 7.9.2 (OSS) node"
echo
