#!/usr/bin/env bash
#

set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning this node"

yum update -y --disableplugin=fastestmirror
yum -y install joe haproxy

#echo 'Copy packages...'
#cp /vagrant/packages/*.rpm /tmp/
#rpm -ivh /tmp/logstash-oss-7.9.2.rpm
#rpm -ivh /tmp/elasticsearch-oss-7.9.2-x86_64.rpm
#rpm -ivh /tmp/kibana-oss-7.9.2-x86_64.rpm

#echo 'Copy configuration files...'
#cp /vagrant/config/ip_to_honeypot_name_mapping.csv /tmp/
#cp /vagrant/config/elasticsearch.yml /etc/elasticsearch/
#cp /vagrant/config/logstash.conf /etc/logstash/conf.d/
#cp /vagrant/config/kibana.yml /etc/kibana/

# Telegraf
#wget https://dl.influxdata.com/telegraf/releases/telegraf-1.8.3-1.x86_64.rpm
#yum -y localinstall telegraf-1.8.3-1.x86_64.rpm
#cp /vagrant/telegraf.conf /etc/telegraf/telegraf.conf

chkconfig haproxy on

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
