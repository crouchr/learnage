#!/usr/bin/env bash
# Bring up the WAF server
# This script is running on the VM itself
# Files on the Host can be accessed via the /vagrant share
# https://tecadmin.net/install-modsecurity-with-apache-on-centos-rhel/

set -e	# bomb out if any problem

echo
echo "[+] Started setup.sh for provisioning this node"

echo "[+] Adding glastopf to hosts file..."
echo "192.168.1.62 glastopf.ermin glastopf" >> /etc/hosts

# Check for patch updates - slows up boot so need a way of avoiding this
yum update -y --disableplugin=fastestmirror
systemctl restart sshd

yum install -y httpd httpd-devel mod_ssl mod_security mod_security_crs
yum install -y mod_security mod_security_crs mod_security-mlogc
#yum install -y mod_ssl

# Add jenkins into apache group so it can upload files
usermod -a -G apache jenkins

echo "[+] Copying core (root-owned) web server configuration and content..."
cp /vagrant/apache/minimal-index.html /var/www/html/index.html
chown apache:apache /var/www/html/index.html
chmod 755 /var/www/html/index.html

echo "[+] Copying Apache configuration..."
cp /vagrant/apache/httpd.conf /etc/httpd/conf/
cp /vagrant/apache/proxy.conf /etc/httpd/conf.d/
cp /vagrant/apache/mod_security.conf /etc/httpd/conf.d/

echo "[+] Adding PaperTrail destination for rsyslog..."
echo "# The following entry was created during box provisioning" > /etc/rsyslog.d/95-papertrail.conf
echo "*.*          @logs2.papertrailapp.com:52491" >> /etc/rsyslog.d/95-papertrail.conf
systemctl restart rsyslog

echo "[+] Starting httpd..."
systemctl start httpd.service
systemctl enable httpd.service

echo "Finished setup.sh OK for provisioning this node"
echo
