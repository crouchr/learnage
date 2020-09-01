#!/usr/bin/env bash
# Bring up the metcrouch web-server
# This script is running on the VM itself
# Files on the Host can be accessed via the /vagrant share

set -e	# bomb out if any problem

echo
echo "[+] Started setup.sh for provisioning this node"

# Check for patch updates - slows up boot so need a way of avoiding this
#yum update -y --disableplugin=fastestmirror
#systemctl restart sshd

yum install -y httpd httpd-devel php php-mysql

# Add jenkins into apache group so it can upload files
#usermod -a -G apache jenkins

echo "[+] Copying core (root-owned) web server configuration and content..."
cp /vagrant/apache/minimal-index.html /var/www/html/index.html
chown apache:apache /var/www/html/index.html
chmod 755 /var/www/html/index.html

cp /vagrant/apache/src/info.php /var/www/html/info.php
chown apache:apache /var/www/html/info.php
chmod 755 /var/www/html/info.php

echo "[+] Copying Apache configuration..."
cp /vagrant/apache/httpd.conf /etc/httpd/conf/

echo "[+] Adding PaperTrail destination for rsyslog..."
echo "# The following entry was created during box provisioning" > /etc/rsyslog.d/95-papertrail.conf
echo "*.*          @logs2.papertrailapp.com:52491" >> /etc/rsyslog.d/95-papertrail.conf
systemctl restart rsyslog

echo "[+] Copying the MetCrouch application..."
cp /vagrant/apache/src/webui.css /var/www/html/webui.css
chown apache:apache /var/www/html/webui.css
chmod 755 /var/www/html/webui.css

cp /vagrant/apache/src/bootstrap.min.css /var/www/html/bootstrap.min.css
chown apache:apache /var/www/html/bootstrap.min.css
chmod 755 /var/www/html/bootstrap.min.css

cp /vagrant/apache/src/jquery.min.js /var/www/html/jquery.min.js
chown apache:apache /var/www/html/jquery.min.js
chmod 755 /var/www/html/jquery.min.js

cp /vagrant/apache/src/index.php /var/www/html/index.php
chown apache:apache /var/www/html/index.php
chmod 755 /var/www/html/index.php


echo "[+] Starting httpd..."
systemctl start httpd.service
systemctl enable httpd.service

echo "Finished setup.sh OK for provisioning this node"
echo
