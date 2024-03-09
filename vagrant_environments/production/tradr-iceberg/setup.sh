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

# MOTD
cp /vagrant/motd/motd /etc/motd

# Allow to run X over SSH
cp /vagrant/config/sshd_config /etc/ssh/sshd_config
pwd

# yum -y install java   # run Jython to run Swing-based UIs
# yum -y install lynx   # local testing of apache

# sound
# yum install mpg123

# Install Python 3.11
#rm -rf /opt/python3
#mkdir /opt/python3
#wget -P /tmp/ https://www.python.org/ftp/python/3.11.6/Python-3.11.6.tgz
#tar xvf /tmp/Python-3.11.6.tgz -C /opt
#cd /opt/Python-3.11.6
#LDFLAGS="${LDFLAGS} -Wl,-rpath=/usr/local/openssl/lib" ./configure --with-openssl=/usr/local/openssl
#make altinstall
#/usr/local/bin/pip3.11 install --upgrade pip

# Apache and PHP for web front end
#yum install -y httpd httpd-devel mod_ssl
#yum install -y mod_security
#yum install -y dnsmasq bind-utils
#yum -y install php php-common php-mysql php-pdo php-intl php-gd php-xml php-mbstring
#echo "date.timezone = Europe/London" >> /etc/php.ini
#mkdir -p /var/www/html/tradr
#chown -R apache:apache /var/www/html/tradr

# TRADR web front-end - move into github so can be updated
cp /vagrant/apache/test.html /var/www/html/tradr/test.html
cp /vagrant/apache/index.php /var/www/html/tradr/index.php
#cp /vagrant/apache/failure.php /var/www/html/tradr/failure.php
#cp /vagrant/apache/success.php /var/www/html/tradr/success.php

# Web Infrastructure code
#cp /vagrant/apache/bootstrap.min.css /var/www/html/tradr/bootstrap.min.css
#cp /vagrant/apache/jquery.min.js /var/www/html/tradr/jquery.min.js
#cp /vagrant/apache/tradr-webui.css /var/www/html/tradr/tradr-webui.css
#chown -R apache:apache /var/www/html/tradr/
#chmod -R 755 /var/www/html/tradr/
#echo "Starting httpd..."
#systemctl enable httpd.service
#systemctl start httpd.service


# Editors
# yum -y install nano

# MariaDB 10.4
#echo -e "[mariadb]\nname=MariaDB Repository\nbaseurl=http://yum.mariadb.org/10.4/centos7-amd64\ngpgcheck=1\ngpgkey=https://yum.mariadb.org/RPM-GPG-KEY-MariaDB" | tee /etc/yum.repos.d/MariaDB.repo
#yum -y install MariaDB-server MariaDB-client MariaDB-devel

#https://www.fosslinux.com/8328/how-to-install-and-configure-grafana-on-centos-7.htm
# Grafana v10.x
#cat <<EOF | sudo tee /etc/yum.repos.d/grafana.repo
#[grafana]
#name=grafana
#baseurl=https://packages.grafana.com/oss/rpm
#repo_gpgcheck=1
#enabled=1
#gpgcheck=1
#gpgkey=https://packages.grafana.com/gpg.key
#sslverify=1
#sslcacert=/etc/pki/tls/certs/ca-bundle.crt
#EOF
#yum -y install grafana
#mkdir -p /etc/grafana
#cp /vagrant/config/grafana.ini /etc/grafana/grafana.ini

#echo "Starting MariaDB..."
#systemctl enable mariadb
#systemctl start mariadb

# FIXME : just leave it insecure for now
##echo "Secure MariaDB..."
##cp /vagrant/scripts/secure_mysql.sh /tmp/secure_mysql.sh
##chmod +x /tmp/secure_mysql.sh
##cd /tmp
##./tmp/secure_my_sql.sh "degenerates"

#echo "Starting Grafana..."
#systemctl enable grafana-server
#systemctl start grafana-server
##systemctl status grafana-server

echo "Finished setup.sh OK for provisioning this node"
# echo "PHP Test Page : http://127.0.0.1:7080/php.ini"
echo "TRADR Research Reports : http://127.0.0.1:7080/tradr/index.php"
echo
