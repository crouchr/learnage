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


# Allow to run X over SSH - add this to the packer file
# cp /vagrant/config/sshd_config /etc/ssh/sshd_config
# pwd

# sound
# yum install mpg123

# Apache and PHP for web front end
# TRADR web front-end - move into github so can be updated
# mkdir -p /var/www/html/tradr/
# cp /vagrant/apache/test.html /var/www/html/tradr/test.html
# cp /vagrant/apache/index.php /var/www/html/tradr/index.php
# cp /vagrant/apache/failure.php /var/www/html/tradr/failure.php
# cp /vagrant/apache/success.php /var/www/html/tradr/success.php

# Web Infrastructure code
# cp /vagrant/apache/bootstrap.min.css /var/www/html/tradr/bootstrap.min.css
# cp /vagrant/apache/jquery.min.js /var/www/html/tradr/jquery.min.js
# cp /vagrant/apache/tradr-webui.css /var/www/html/tradr/tradr-webui.css
# chown -R apache:apache /var/www/html/tradr/
# chmod -R 755 /var/www/html/tradr/

# FIXME : just leave it insecure for now
## echo "Secure MariaDB..."
## cp /vagrant/scripts/secure_mysql.sh /tmp/secure_mysql.sh
## chmod +x /tmp/secure_mysql.sh
## cd /tmp
## ./tmp/secure_my_sql.sh "degenerates"


echo "Finished setup.sh OK for provisioning this node"
# echo "PHP Test Page : http://127.0.0.1:7080/php.ini"
# echo "TRADR Research Reports : http://127.0.0.1:7080/tradr/index.php"
echo
