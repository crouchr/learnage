#!/usr/bin/env bash
# Bring up the Apache server as a reverse proxy
# This script is running on the VM itself
# Files on the Host can be accessed via the /vagrant share

set -e	# bomb out if any problem

echo
echo "[+] Started setup.sh for provisioning this node"

#echo "[+] Adding glastopf to hosts file..."
#echo "192.168.1.62 glastopf.ermin glastopf" >> /etc/hosts

echo "[+] Adding XW6600 webserver to hosts file..."
echo "192.168.1.15 erminserver.ermin erminserver" >> /etc/hosts

# Check for patch updates - slows up boot so need a way of avoiding this
yum update -y --disableplugin=fastestmirror
systemctl restart sshd

yum install -y httpd httpd-devel mod_ssl

echo "[+] Create directory for self-signed certificate..."
cd /etc/ssl
mkdir /etc/ssl/private
chmod 700 /etc/ssl/private

echo "[+] Copying core (root-owned) web server configuration and content..."
cp /vagrant/apache/index.html /var/www/html/index.html
chown apache:apache /var/www/html/index.html
chmod 755 /var/www/html/index.html

echo "[+] Copying Apache configuration..."
cp /vagrant/apache/httpd.conf /etc/httpd/conf/
cp /vagrant/apache/proxy.conf /etc/httpd/conf.d/
cp /vagrant/apache/ssl.conf /etc/httpd/conf.d/

echo "[+] Copy SSL cert generation script (run manually)..."
cp /vagrant/apache/create_selfsigned_cert_centos7.sh /tmp/

echo "[+] Copy self-signed certificate..."
yes | cp -rf /vagrant/certs/*.crt /etc/ssl/certs
yes | cp -rf /vagrant/certs/*.key /etc/ssl/private

echo "[+] Adding PaperTrail destination for rsyslog..."
echo "# The following entry was created during box provisioning" > /etc/rsyslog.d/95-papertrail.conf
echo "*.*          @logs2.papertrailapp.com:52491" >> /etc/rsyslog.d/95-papertrail.conf
systemctl restart rsyslog

echo "[+] Starting httpd..."
systemctl start httpd.service
systemctl enable httpd.service

echo "Finished setup.sh OK for provisioning this node"
echo
