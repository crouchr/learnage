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

# Needed for mariadb-connector-c
yum install -y http://repo.okay.com.mx/centos/7/x86_64/release/okay-release-1-1.noarch.rpm

echo "[+] Install CentOS7 package dependencies..."
yum install -y python3 python3-devel
yum install -y mariadb-server
yum install -y mariadb-libs
yum install -y mariadb-devel
yum install -y mariadb-connector-c

echo "[+] Install Database Python dependencies..."
pip3 install mysql-connector-python

echo "[+] Install misc Python dependencies..."
pip3 install requests Flask ConfigParser pytest

echo "[+] Install Apache..."
yum install -y httpd httpd-devel php php-mysql

echo "[+] Install MariaDB scripts..."
cp /vagrant/mariadb/mariadb.sh /home/vagrant/mariadb.sh
chown vagrant:vagrant /home/vagrant/mariadb.sh
chmod 755 /home/vagrant/mariadb.sh

echo "[+] Create dir to hold web app..."
mkdir /opt/minimet
chown apache:apache /opt/minimet
chmod 755 /opt/minimet

echo "[+] Copying core (root-owned) web server configuration and content..."
cp /vagrant/apache/minimal-index.html /var/www/html/index.html
chown apache:apache /var/www/html/index.html
chmod 755 /var/www/html/index.html

cp /vagrant/apache/src/info.php /var/www/html/info.php
chown apache:apache /var/www/html/info.php
chmod 755 /var/www/html/info.php

echo "[+] Copying Apache configuration..."
cp /vagrant/apache/httpd.conf /etc/httpd/conf/

#echo "[+] Adding PaperTrail destination for rsyslog..."
#echo "# The following entry was created during box provisioning" > /etc/rsyslog.d/95-papertrail.conf
#echo "*.*          @logs2.papertrailapp.com:52491" >> /etc/rsyslog.d/95-papertrail.conf
#systemctl restart rsyslog

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

cp /vagrant/apache/src/success.php /var/www/html/success.php
chown apache:apache /var/www/html/success.php
chmod 755 /var/www/html/success.php

cp /vagrant/apache/src/failure.php /var/www/html/failure.php
chown apache:apache /var/www/html/failure.php
chmod 755 /var/www/html/failure.php

# -------
cp /vagrant/apache/src/actuald.py /opt/minimet/actuald.py
chown apache:apache /opt/minimet/actuald.py
chmod 755 /opt/minimet/actuald.py

cp /vagrant/apache/src/app.py /opt/minimet/app.py
chown apache:apache /opt/minimet/app.py
chmod 755 /opt/minimet/app.py

cp /vagrant/apache/src/config.py /opt/minimet/config.py
chown apache:apache /opt/minimet/config.py
chmod 755 /opt/minimet/config.py

cp /vagrant/apache/src/connect_db.py /opt/minimet/connect_db.py
chown apache:apache /opt/minimet/connect_db.py
chmod 755 /opt/minimet/connect_db.py

cp /vagrant/apache/src/current_weather.py /opt/minimet/current_weather.py
chown apache:apache /opt/minimet/current_weather.py
chmod 755 /opt/minimet/current_weather.py

cp /vagrant/apache/src/data_logging.py /opt/minimet/data_logging.py
chown apache:apache /opt/minimet/data_logging.py
chmod 755 /opt/minimet/data_logging.py

cp /vagrant/apache/src/delete_rec_from_db.py /opt/minimet/delete_rec_from_db.py
chown apache:apache /opt/minimet/delete_rec_from_db.py
chmod 755 /opt/minimet/delete_rec_from_db.py

cp /vagrant/apache/src/export_rec_from_db.py /opt/minimet/export_rec_from_db.py
chown apache:apache /opt/minimet/export_rec_from_db.py
chmod 755 /opt/minimet/export_rec_from_db.py

cp /vagrant/apache/src/forecaster.py /opt/minimet/forecaster.py
chown apache:apache /opt/minimet/forecaster.py
chmod 755 /opt/minimet/forecaster.py

cp /vagrant/apache/src/funcs.py /opt/minimet/funcs.py
chown apache:apache /opt/minimet/funcs.py
chmod 755 /opt/minimet/funcs.py

cp /vagrant/apache/src/julian.py /opt/minimet/julian.py
chown apache:apache /opt/minimet/julian.py
chmod 755 /opt/minimet/julian.py

cp /vagrant/apache/src/locations.py /opt/minimet/locations.py
chown apache:apache /opt/minimet/locations.py
chmod 755 /opt/minimet/locations.py

cp /vagrant/apache/src/met_funcs.py /opt/minimet/met_funcs.py
chown apache:apache /opt/minimet/met_funcs.py
chmod 755 /opt/minimet/met_funcs.py

cp /vagrant/apache/src/predictord.py /opt/minimet/predictord.py
chown apache:apache /opt/minimet/predictord.py
chmod 755 /opt/minimet/predictord.py

cp /vagrant/apache/src/trend.py /opt/minimet/trend.py
chown apache:apache /opt/minimet/trend.py
chmod 755 /opt/minimet/trend.py

cp /vagrant/apache/src/ts_funcs.py /opt/minimet/ts_funcs.py
chown apache:apache /opt/minimet/ts_funcs.py
chmod 755 /opt/minimet/ts_funcs.py

cp /vagrant/apache/src/ts_funcs.py /opt/minimet/twitter.py
chown apache:apache /opt/minimet/twitter.py
chmod 755 /opt/minimet/twitter.py

cp /vagrant/apache/src/app.py /opt/minimet/minimet.ini
chown apache:apache /opt/minimet/minimet.ini
chmod 755 /opt/minimet/minimet.ini

cp /vagrant/mariadb/mariadb.sh /tmp/mariadb.sh
chown apache:apache /tmp/mariadb.sh
chmod 755 /tmp/mariadb.sh

cp /vagrant/mariadb/mariadb_test.sh /tmp/mariadb_test.sh
chown apache:apache /tmp/mariadb_test.sh
chmod 755 /tmp/mariadb_test.sh

echo "[+] Starting MariaDB..."
systemctl start mariadb
systemctl enable mariadb

echo "[+] Starting httpd..."
systemctl start httpd.service
systemctl enable httpd.service

echo "Finished setup.sh OK for provisioning this node"
echo

