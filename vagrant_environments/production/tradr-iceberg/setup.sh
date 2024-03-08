#!/usr/bin/env bash
# This script is running on the VM itself
# Files on the Host can be accessed via the /vagrant share
# https://www.urban-software.com/cacti-howtos/howto-install-influxdb-on-centos/
# grafana : initial account is admin/admin
# influxdb and telegraf written by same team

set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning this node"

# Check for patch updates - slows up boot so need a way of avoiding this
yum update -y --disableplugin=fastestmirror

# Need accurate time
yum -y install ntp
echo "Starting NTPd..."
systemctl enable ntpd
systemctl start ntpd


echo -e "[mariadb]\nname=MariaDB Repository\nbaseurl=http://yum.mariadb.org/10.4/centos7-amd64\ngpgcheck=1\ngpgkey=https://yum.mariadb.org/RPM-GPG-KEY-MariaDB" | tee /etc/yum.repos.d/MariaDB.repo


# MariaDB 10.4 Python 3.6

yum -y install MariaDB-server MariaDB-client MariaDB-devel python3

# InfluxDB
#cat <<EOF | sudo tee /etc/yum.repos.d/influxdb.repo
#[influxdb]
#name = InfluxDB Repository - RHEL \$releasever
#baseurl = https://repos.influxdata.com/rhel/\$releasever/\$basearch/stable
#enabled = 1
#gpgcheck = 1
#gpgkey = https://repos.influxdata.com/influxdb.key
#EOF

#yum -y install influxdb
#mkdir -p /etc/influxdb
#cp /vagrant/influxdb.conf /etc/influxdb/influxdb.conf

#https://www.fosslinux.com/8328/how-to-install-and-configure-grafana-on-centos-7.htm
# Grafana v7.x
cat <<EOF | sudo tee /etc/yum.repos.d/grafana.repo
[grafana]
name=grafana
baseurl=https://packages.grafana.com/oss/rpm
repo_gpgcheck=1
enabled=1
gpgcheck=1
gpgkey=https://packages.grafana.com/gpg.key
sslverify=1
sslcacert=/etc/pki/tls/certs/ca-bundle.crt
EOF
yum -y install grafana
mkdir -p /etc/grafana
cp /vagrant/config/grafana.ini /etc/grafana/grafana.ini

echo "Starting MariaDB..."
systemctl enable mariadb
systemctl start mariadb

echo "Secure MariaDB..."
cp /vagrant/scripts/secure_mysql.sh /tmp/secure_mysql.sh
chmod +x /tmp/secure_mysql.sh
cd /tmp
./secure_my_sql.sh "tradrthemoon"

echo "Starting Grafana..."
systemctl enable grafana-server
systemctl start grafana-server
##systemctl status grafana-server

echo "Finished setup.sh OK for provisioning this node"
echo
