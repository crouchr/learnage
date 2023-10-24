#!/usr/bin/env bash
# https://www.digitalocean.com/community/tutorials/how-to-install-mariadb-on-centos-7
set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning this node"

# Check for patch updates - slows up boot so need a way of avoiding this
#yum update -y --disableplugin=fastestmirror
#systemctl restart sshd

yum install -y mariadb-server

echo "Starting MariaDB..."
systemctl enable mariadb
systemctl start mariadb

echo "Secure MariaDB..."
cp /vagrant/secure_mysql.sh /tmp/secure_mysql.sh
chmod +x /tmp/secure_mysql.sh
cd /tmp
./secure_my_sql.sh "secretsql"

echo "Finished setup.sh OK for provisioning this node"
echo
