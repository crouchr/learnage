#!/usr/bin/env bash
# OSSEC Server plus WUI plus MariaDB plus ClamAV
# Built on CentOS7
# Add interface to Cuckoo malware submission ?

# PHP 5.x install https://www.tecmint.com/install-php-5-6-on-centos-7/
# https://www.hostinger.co.uk/tutorials/how-to-install-clamav-centos7
set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning this node"

# add repos for PHP5.X
#yum install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
yum install -y http://rpms.remirepo.net/enterprise/remi-release-7.rpm
yum-config-manager --enable remi-php56

yum update -y --disableplugin=fastestmirror
yum install -y mariadb-server mariadb-devel
yum install -y httpd httpd-devel mod_ssl
yum install -y clamav-server clamav-data clamav-update clamav-filesystem clamav clamav-scanner-systemd clamav-devel clamav-lib clamav-server-systemd
yum install -y php php-mcrypt php-cli php-gd php-curl php-mysql php-ldap php-zip php-fileinfo
yum install -y GeoIP-devel unzip
yum install -y yum-utils

# Add jenkins into apache group so it can upload files
# usermod -a -G apache jenkins

mkdir -p /var/www/html/uploads
chown -R apache:apache /var/www/html/uploads
# Allow members of apache group (e.g. jenkins user) to upload to this directory
chmod 775 /var/www/html/uploads

echo "Copying core (root-owned) web server configuration and content..."
cp /vagrant/apache/minimal-index.html /var/www/html/index.html
chown apache:apache /var/www/html/index.html
chmod 755 /var/www/html/index.html
cp /vagrant/apache/minimal-httpd.conf /etc/httpd/httpd.conf

mkdir -p /var/ossec/etc

echo 'Copy sources...'
cp /vagrant/sources/ossec-hids-2.8.3.tar.gz /tmp/
cp /vagrant/installer/build.sh /tmp/
cp /vagrant/sources/ossec-wui-master.zip /tmp/
cp /vagrant/sources/GeoLiteCity.dat /var/ossec/etc/

# Now vagrant ssh into the node
# vagrant ssh
echo "Starting httpd..."
systemctl enable httpd.service
systemctl start httpd.service


# sudo su -
# cd /tmp
# chmod +x build.sh
# ./build.sh

# server mode
# no email alerting
# no active response
# syscheck - until production ready
# rootkit detection - until production ready
# no logging to udp 514 - i.e. only use encrypted channel via agents


# install wui
# cd /tmp
# unzip ossec-wui-master.zip
# mv ossec-wui-master /var/www/ossec-wui
# mv /var/www/ossec-wui/ /var/www/html/
# cd /var/www/ossec-wui
# ./setup.sh

# username : crouch
# password : <solar>
# run as apache
# usermod -G ossec apache
# chmod 770 /tmp
# chgrp apache /tmp

# systemctl restart httpd


# here is the error
# Not Found
#
# The requested URL /ossec-wui/ was not found on this server.




# /tmp/ossec-hids-2.9.3/install.sh
#
# - In order to connect agent and server, you need to add each agent to the server.
#   Run the 'manage_agents' to add or remove them:
#
#   /var/ossec/bin/manage_agents

echo "Finished setup.sh OK for provisioning this node"
echo
