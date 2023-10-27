#!/usr/bin/env bash
# OSSEC

set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning this node"

yum update -y --disableplugin=fastestmirror

#yum -y install bind bind-utils
#systemctl start named
#systemctl enable named
#systemctl status named #Should show active

#yum -y install java-1.8.0-openjdk.x86_64
# cp /vagrant/config.yml /etc/docker-distribution/registry/config.yml

# ELK
#wget -O /tmp/elasticsearch-7.9.2-x86_64.rpm https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.9.2-x86_64.rpm
#rpm -ivh /tmp/elasticsearch-7.9.2-x86_64.rpm
#yum -y localinstall elasticsearch-7.9.2-x86_64.rpm

echo 'Copy packages...'
cp /vagrant/sources/ossec-hids-2.8.3.tar.gz /tmp/
#rpm -ivh /tmp/logstash-oss-7.9.2.rpm
#rpm -ivh /tmp/elasticsearch-oss-7.9.2-x86_64.rpm
#rpm -ivh /tmp/kibana-oss-7.9.2-x86_64.rpm

tar xvf /tmp/ossec-hids-2.8.3.tar.gz
#/tmp/ossec-hids-2.8.3/install.sh
# - In order to connect agent and server, you need to add each agent to the server.
#   Run the 'manage_agents' to add or remove them:
#
#   /var/ossec/bin/manage_agents

#echo 'Copy BIND configuration files...'
#cp /vagrant/config/named.conf /etc/
#cp /vagrant/config/ermin.lan.db /var/named/
#cp /vagrant/config/192.168.1.db /var/named/

#echo 'Copy BIND check scripts...'
#chmod +x /vagrant/scripts/bind_checks.sh
#cp /vagrant/scripts/bind_checks.sh /home/vagrant/

#cp /vagrant/config/elasticsearch.yml /etc/elasticsearch/
#cp /vagrant/config/logstash.conf /etc/logstash/conf.d/
#cp /vagrant/config/kibana.yml /etc/kibana/

# Telegraf
#wget https://dl.influxdata.com/telegraf/releases/telegraf-1.8.3-1.x86_64.rpm
#yum -y localinstall telegraf-1.8.3-1.x86_64.rpm
#cp /vagrant/telegraf.conf /etc/telegraf/telegraf.conf

#echo "Enable DNS services..."
#sudo systemctl start named
#sudo systemctl enable named
#sudo systemctl status named

#echo "Enable ELK services..."
#sudo systemctl enable logstash.service
#sudo systemctl enable elasticsearch.service
#sudo systemctl enable kibana.service

#echo "Start ELK services..."
#sudo systemctl start elasticsearch.service
#sudo systemctl start logstash.service
#sudo systemctl start kibana.service

echo "Finished setup.sh OK for provisioning this node"
echo
