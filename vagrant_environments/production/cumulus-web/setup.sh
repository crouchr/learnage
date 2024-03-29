#!/usr/bin/env bash
# Bring up the Cumulus web server
# This script assumes a CentOS host
# Files on the Host can be accessed via the /vagrant share
# DNS info : https://www.tecmint.com/setup-a-dns-dhcp-server-using-dnsmasq-on-centos-rhel/

set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning this node"

# Check for patch updates - slows up boot so need a way of avoiding this
#yum update -y --disableplugin=fastestmirror
#systemctl restart sshd

yum install -y httpd httpd-devel mod_ssl python-pip
#yum install -y dnsmasq bind-utils

yum -y install php php-common
#php-mysql php-pdo php-intl php-gd php-xml php-mbstring
#echo "Include /vagrant/apache/*.conf" >> /etc/httpd/conf/httpd.conf

# Install PIP
#pip install --upgrade pip
pip install wheel

# Generate metadata.json - no longer needed
#pip install vagrant-metadata

echo "date.timezone = Europe/London" >> /etc/php.ini

# Add jenkins into apache group so it can upload files
#usermod -a -G apache jenkins
mkdir -p /var/www/html/cumulus
chown -R apache:apache /var/www/html/cumulus

#mkdir -p /var/www/html/uploads
#chown -R apache:apache /var/www/html/uploads
# Allow members of apache group (e.g. jenkins user) to upload to this directory
#chmod 775 /var/www/html/uploads
#
#mkdir -p /var/www/html/public-keys
#chown -R apache:apache /var/www/html/public-keys

#mkdir -p /var/www/html/isos
#chown -R apache:apache /var/www/html/isos
#
#mkdir -p /var/www/html/br2020-packages
#chown -R apache:apache /var/www/html/br2020-packages
#
#mkdir -p /var/www/html/slackware-14-2-packages
#chown -R apache:apache /var/www/html/slackware-14-2-packages
#
#mkdir -p /var/www/html/python-packages/metfuncs
#chown -R apache:apache /var/www/html/python-packages/metfuncs
#
#mkdir -p /var/www/html/br-mal-files
#chown -R apache:apache /var/www/html/br-mal-files
#
#mkdir -p /var/www/html/private/bootstrap-chef-files
#chown -R apache:apache /var/www/html/private

echo "Copying core (root-owned) web server configuration and content..."
cp /vagrant/apache/minimal-index.html /var/www/html/index.html
chown apache:apache /var/www/html/index.html
chmod 755 /var/www/html/index.html

cp /vagrant/apache/minimal-httpd.conf /etc/httpd/httpd.conf

# Copy DNSMASQ files
#cp /vagrant/dnsmasq/dnsmasq.conf /etc/dnsmasq.conf
#cp /vagrant/dnsmasq/hosts /etc/hosts

# Make immutable - so that NetworkManager can't override setting
#chattr -i /etc/resolv.conf
#cp /vagrant/dnsmasq/resolv.conf /etc/resolv.conf
#chattr +i /etc/resolv.conf

# Store ISOs used for Vagrant locally 
#echo "Copying ISO images..."
#cp /vagrant/apache/isos/*.iso /var/www/html/isos/
#chmod 755 /var/www/html/isos/*

#echo "Copying Python packages..."
#cp /vagrant/apache/python-packages/metfuncs/*.tar.gz /var/www/html/python-packages/metfuncs/
#cp /vagrant/apache/python-packages/metfuncs/*.whl /var/www/html/python-packages/metfuncs/
#chmod 755 /var/www/html/br2020-packages/*
#chmod 755 /var/www/html/slackware-14-2-packages/*

#echo "Starting dnsmasq..."
#systemctl enable dnsmasq.service
#systemctl start dnsmasq.service

echo "Starting httpd..."
systemctl enable httpd.service
systemctl start httpd.service

echo "Finished setup.sh OK for provisioning this cumulusmx web-server node"
echo
