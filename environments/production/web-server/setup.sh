#!/usr/bin/env bash
# Bring up the web server
# This script is running on the VM itself
# Files on the Host can be accessed via the /vagrant share

set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning this node"

# Check for patch updates - slows up boot so need a way of avoiding this
#yum update -y --disableplugin=fastestmirror
#systemctl restart sshd

yum install -y httpd httpd-devel mod_ssl python-pip

#yum -y install php php-common php-mysql php-pdo php-intl php-gd php-xml php-mbstring
#echo "Include /vagrant/apache/*.conf" >> /etc/httpd/conf/httpd.conf

# Install PIP
pip install --upgrade pip
pip install wheel

# Generate metadata.json
pip install vagrant-metadata

#echo "date.timezone = Europe/London" >> /etc/php.ini

# Add jenkins into apache group so it can upload files
usermod -a -G apache jenkins

mkdir -p /var/www/html/uploads
chown -R apache:apache /var/www/html/uploads
# Allow members of apache group (e.g. jenknis user) to upload to this directory
chmod 775 /var/www/html/uploads

mkdir -p /var/www/html/public-keys
chown -R apache:apache /var/www/html/public-keys

mkdir -p /var/www/html/isos
chown -R apache:apache /var/www/html/isos

mkdir -p /var/www/html/br2020-packages
chown -R apache:apache /var/www/html/br2020-packages

mkdir -p /var/www/html/private/bootstrap-chef-files
chown -R apache:apache /var/www/html/private

mkdir -p /var/www/html/boxes/nvm-centos7/0.0.2/virtualbox
chown -R apache:apache /var/www/html/boxes
chmod -R 775 /var/www/html/boxes/nvm-centos7/0.0.2/virtualbox

echo "Copying core (root-owned) web server configuration and content..."
cp /vagrant/apache/minimal-index.html /var/www/html/index.html
chown apache:apache /var/www/html/index.html
chmod 755 /var/www/html/index.html

cp /vagrant/apache/minimal-httpd.conf /etc/httpd/httpd.conf

# Copy the NVM CentOS7 box across as this is not built on my nodes
echo "Copying NVM Jenkins-built CentOS7..."
cp /vagrant/apache/boxes/CentOS7_v2_virtualbox.box /var/www/html/boxes/nvm-centos7/0.0.2/virtualbox/
chmod 755 /var/www/html/boxes/nvm-centos7/0.0.2/virtualbox/*
 
# Store ISOs used for Vagrant locally 
echo "Copying ISO images..."
cp /vagrant/apache/isos/*.iso /var/www/html/isos/
chmod 755 /var/www/html/isos/*

# Store BR2020 packages 
echo "Copying BR2020 CentOS7 packages and source code..."
cp /vagrant/apache/br2020-packages/*.rpm /var/www/html/br2020-packages/
cp /vagrant/apache/br2020-packages/*.tar.gz /var/www/html/br2020-packages/
cp /vagrant/apache/br2020-packages/*.tgz /var/www/html/br2020-packages/
cp /vagrant/apache/br2020-packages/*.dat.gz /var/www/html/br2020-packages/
cp /vagrant/apache/br2020-packages/*.zip /var/www/html/br2020-packages/
chmod 755 /var/www/html/br2020-packages/*

# Store public keys on web server for easy retrieval 
echo "Copying public-keys..."
cp /vagrant/apache/public-keys/*.pub /var/www/html/public-keys/
chmod 755 /var/www/html/public-keys/*.pub

# Store Chef files 
echo "Copying Chef configuration files and keys..."
cp /vagrant/apache/bootstrap-chef-files/* /var/www/html/private/bootstrap-chef-files/
chmod 755 /var/www/html/private/bootstrap-chef-files/*

# Generate the metadata.json file for the NVM Jenkins-built Centos7 image
echo "Generating NVM CentOS7 box file metadata.json..."
cd /var/www/html/boxes/nvm-centos7
rm -f metadata.json
vagrant-metadata \
--name="web.ermin/nvm-centos7" \
--description="NVM Centos7" \
--baseurl="http://web.ermin/boxes/nvm-centos7"

echo "Starting httpd..."
systemctl start httpd.service
systemctl enable httpd.service

echo "Finished setup.sh OK for provisioning this node"
echo
