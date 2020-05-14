#!/usr/bin/env bash
# Bring up the WAF server
# This script is running on the VM itself
# Files on the Host can be accessed via the /vagrant share
# https://tecadmin.net/install-modsecurity-with-apache-on-centos-rhel/

set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning this node"

# Check for patch updates - slows up boot so need a way of avoiding this
yum update -y --disableplugin=fastestmirror
systemctl restart sshd

yum install -y httpd httpd-devel mod_ssl mod_security mod_security_crs
#yum install -y mod_security mod_security_crs
#yum install -y mod_ssl
#yum install python-pip

#yum -y install php php-common php-mysql php-pdo php-intl php-gd php-xml php-mbstring
#echo "Include /vagrant/apache/*.conf" >> /etc/httpd/conf/httpd.conf

# Install PIP
#pip install --upgrade pip
#pip install wheel

#echo "date.timezone = Europe/London" >> /etc/php.ini

# Add jenkins into apache group so it can upload files
usermod -a -G apache jenkins

echo "Copying core (root-owned) web server configuration and content..."
cp /vagrant/apache/minimal-index.html /var/www/html/index.html
chown apache:apache /var/www/html/index.html
chmod 755 /var/www/html/index.html

echo "Copying Apache configuration..."
cp /vagrant/apache/httpd.conf /etc/httpd/conf/
cp /vagrant/apache/proxy.conf /etc/httpd/conf.d/
#cp /vagrant/apache/mod_security.conf /etc/httpd/conf.d/

echo "Starting httpd..."
systemctl start httpd.service
systemctl enable httpd.service

echo "Finished setup.sh OK for provisioning this node"
echo
