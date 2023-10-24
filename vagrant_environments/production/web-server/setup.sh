#!/usr/bin/env bash
# Bring up the web server
# This script assumes a CentOS host
# Files on the Host can be accessed via the /vagrant share
# DNS info : https://www.tecmint.com/setup-a-dns-dhcp-server-using-dnsmasq-on-centos-rhel/

set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning this node v1.0.0"

# Check for patch updates - slows up boot so need a way of avoiding this
yum update -y --disableplugin=fastestmirror

yum install -y python-pip
pip install --upgrade pip==20.3.4  # last version to support Python2

yum install -y httpd httpd-devel mod_ssl
yum install -y mod_security
yum install -y dnsmasq bind-utils

#yum -y install php php-common php-mysql php-pdo php-intl php-gd php-xml php-mbstring
#echo "Include /vagrant/apache/*.conf" >> /etc/httpd/conf/httpd.conf

# Install Wheel
#pip install --upgrade pip
pip install wheel

# Generate metadata.json - no longer needed
#pip install vagrant-metadata

#echo "date.timezone = Europe/London" >> /etc/php.ini

# Add jenkins into apache group so it can upload files
usermod -a -G apache jenkins

mkdir -p /var/www/html/uploads
chown -R apache:apache /var/www/html/uploads
# Allow members of apache group (e.g. jenkins user) to upload to this directory
chmod 775 /var/www/html/uploads

mkdir -p /var/www/html/public-keys
chown -R apache:apache /var/www/html/public-keys

mkdir -p /var/www/html/isos
chown -R apache:apache /var/www/html/isos

mkdir -p /var/www/html/br2020-packages
chown -R apache:apache /var/www/html/br2020-packages

mkdir -p /var/www/html/centos7-packages
chown -R apache:apache /var/www/html/centos7-packages

mkdir -p /var/www/html/slackware-14-2-packages
chown -R apache:apache /var/www/html/slackware-14-2-packages

mkdir -p /var/www/html/source-code
chown -R apache:apache /var/www/html/source-code

mkdir -p /var/www/html/python-packages/metfuncs
chown -R apache:apache /var/www/html/python-packages/metfuncs
mkdir -p /var/www/html/python-packages/metrestapi
chown -R apache:apache /var/www/html/python-packages/metrestapi
mkdir -p /var/www/html/python-packages/metminifuncs
chown -R apache:apache /var/www/html/python-packages/metminifuncs
mkdir -p /var/www/html/python-packages/cryptofuncs
chown -R apache:apache /var/www/html/python-packages/cryptofuncs
mkdir -p /var/www/html/python-packages/mqttfuncs
chown -R apache:apache /var/www/html/python-packages/mqttfuncs
mkdir -p /var/www/html/python-packages/vonageapi
chown -R apache:apache /var/www/html/python-packages/vonageapi

mkdir -p /var/www/html/br-mal-files
chown -R apache:apache /var/www/html/br-mal-files

mkdir -p /var/www/html/private/bootstrap-chef-files
chown -R apache:apache /var/www/html/private

echo "Copying core (root-owned) web server configuration and content..."
cp /vagrant/apache/minimal-index.html /var/www/html/index.html
chown apache:apache /var/www/html/index.html
chmod 755 /var/www/html/index.html

cp /vagrant/apache/minimal-httpd.conf /etc/httpd/httpd.conf

# Copy DNSMASQ files
cp /vagrant/dnsmasq/dnsmasq.conf /etc/dnsmasq.conf
cp /vagrant/dnsmasq/hosts /etc/hosts

# Make immutable - so that NetworkManager can't override setting
chattr -i /etc/resolv.conf
cp /vagrant/dnsmasq/resolv.conf /etc/resolv.conf
chattr +i /etc/resolv.conf

# Store ISOs used for Vagrant locally 
# Always store Packer ISOs on the Jenkins Packer build agent directly otherwise it take hours to just download them
# echo "Copying ISO images..."
# cp /vagrant/apache/isos/*.iso /var/www/html/isos/
# chmod 755 /var/www/html/isos/*

# Store CentOS7 packages
echo "Copying CentOS7 packages..."
cp /vagrant/apache/centos7-packages/*.rpm /var/www/html/centos7-packages/

# Store BR2020 packages
echo "Copying test malware files..."
cp /vagrant/apache/br-mal-files/* /var/www/html/br-mal-files/

# Store BR2020 packages
echo "Copying BR2020 CentOS7 packages and source code..."
cp /vagrant/apache/br2020-packages/*.rpm /var/www/html/br2020-packages/
cp /vagrant/apache/br2020-packages/*.bz2 /var/www/html/br2020-packages/
cp /vagrant/apache/br2020-packages/*.tar.gz /var/www/html/br2020-packages/
cp /vagrant/apache/br2020-packages/*.tgz /var/www/html/br2020-packages/
cp /vagrant/apache/br2020-packages/*.dat.gz /var/www/html/br2020-packages/
cp /vagrant/apache/br2020-packages/*.zip /var/www/html/br2020-packages/
cp /vagrant/apache/br2020-packages/*.json /var/www/html/br2020-packages/
cp /vagrant/apache/br2020-packages/*.repo /var/www/html/br2020-packages/
cp /vagrant/apache/br2020-packages/*.conf /var/www/html/br2020-packages/
cp /vagrant/apache/br2020-packages/config-generic* /var/www/html/br2020-packages/
#cp /vagrant/apache/br2020-packages/*.patch /var/www/html/br2020-packages/
#cp /vagrant/apache/br2020-packages/*.msi /var/www/html/br2020-packages/
#cp /vagrant/apache/br2020-packages/*.hpi /var/www/html/br2020-packages/
#cp /vagrant/apache/br2020-packages/trojan-bash /var/www/html/br2020-packages/
#cp /vagrant/apache/br2020-packages/afterglow.pl /var/www/html/br2020-packages/

# Store generic source code packages
#echo "Copying source code..."
#cp /vagrant/apache/source-code/*.tar.gz /var/www/html/source-code/
#chmod 755 /var/www/html/source-code/*

echo "Copying Slackware 14.2 packages..."
cp /vagrant/apache/slackware-14-2-packages/*.tgz /var/www/html/slackware-14-2-packages/

# https://serverfault.com/questions/153875/how-to-let-cp-command-dont-fire-an-error-when-source-file-does-not-exist
#echo "Copying Python packages into my artifacts..."
cp /vagrant/apache/python-packages/metfuncs/*.tar.gz /var/www/html/python-packages/metfuncs/
cp /vagrant/apache/python-packages/metfuncs/*.whl /var/www/html/python-packages/metfuncs/
#cp /vagrant/apache/python-packages/metrestapi/*.tar.gz /var/www/html/python-packages/metrestapi/
#cp /vagrant/apache/python-packages/metrestapi/*.whl /var/www/html/python-packages/metrestapi/
cp /vagrant/apache/python-packages/metminifuncs/*.tar.gz /var/www/html/python-packages/metminifuncs/
cp /vagrant/apache/python-packages/metminifuncs/*.whl /var/www/html/python-packages/metminifuncs/
cp /vagrant/apache/python-packages/cryptofuncs/*.whl /var/www/html/python-packages/cryptofuncs/
#cp /vagrant/apache/python-packages/mqttfuncs/*.whl /var/www/html/python-packages/mqttfuncs/
#cp /vagrant/apache/python-packages/vonageapi/*.whl /var/www/html/python-packages/vonageapi/

chmod 755 /var/www/html/br2020-packages/*
#chmod 755 /var/www/html/slackware-14-2-packages/*

# Store public keys on web server for easy retrieval
echo "Copying public-keys..."
cp /vagrant/apache/public-keys/*.pub /var/www/html/public-keys/
chmod 755 /var/www/html/public-keys/*.pub

# Store Chef files
# Commented out until design is worked out
#echo "Copying Chef configuration files and keys..."
#cp /vagrant/apache/bootstrap-chef-files/* /var/www/html/private/bootstrap-chef-files/
#chmod 755 /var/www/html/private/bootstrap-chef-files/*

echo "Starting dnsmasq..."
systemctl enable dnsmasq.service
systemctl start dnsmasq.service

echo "Starting httpd..."
systemctl enable httpd.service
systemctl start httpd.service

echo "Finished setup.sh OK for provisioning this web-server node"
echo
