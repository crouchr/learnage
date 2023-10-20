#!/usr/bin/env bash
# Bring up the Gitea server
# This script assumes a CentOS host
# This script requires human intervention but then the machine can be saved as a OVA file

# see https://www.vultr.com/docs/how-to-install-gitea-on-centos-7/

set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning Gitea node"

# Check for patch updates - slows up boot so need a way of avoiding this
yum update -y --disableplugin=fastestmirror

yum install -y joe git mariadb-server

# Configure node
#cp /vagrant/squid/squid.conf /etc/squid/squid.conf
#cp /vagrant/squid/cloud.cfg /etc/cloud/cloud.cfg

# FIXME : not working
# cp /vagrant/gitea/config/gitea.service /etc/systemd/system/gitea.service

echo "Starting MariaDB..."
systemctl enable mariadb.service
systemctl start mariadb.service

# Configure MariaDB
# How to automate this ?
# https://bertvv.github.io/notes-to-self/2015/11/16/automating-mysql_secure_installation/
# mysql_secure_installation
# example with password in env var
#UPDATE mysql.user SET Password=PASSWORD('${db_root_password}') WHERE User='root';

# Secure the database i.e. equivalent to mysql_secure_installation
myql --user=root <<_EOF_
UPDATE mysql.user SET Password=PASSWORD('password123') WHERE User='root';
DELETE FROM mysql.user WHERE User='';
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');
DROP DATABASE IF EXISTS test;
DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';
FLUSH PRIVILEGES;
_EOF_

# Enter current password for root (enter for none): Just press the Enter
# Set root password? [Y/n]: Y
# New password: Enter password
# Re-enter new password: Repeat password
# Remove anonymous users? [Y/n]: Y
# Disallow root login remotely? [Y/n]: Y
# Remove test database and access to it? [Y/n]:  Y
# Reload privilege tables now? [Y/n]:  Y

systemctl restart mariadb.service

myql --user=root --password 'password123' <<_EOF_
CREATE DATABASE gitea;
CREATE USER 'giteauser'@'localhost' IDENTIFIED BY 'new_password_here';
GRANT ALL ON gitea.* TO 'giteauser'@'localhost' IDENTIFIED BY 'user_password_here' WITH GRANT OPTION;
FLUSH PRIVILEGES;
_EOF_

# mysql -u root -p
# CREATE DATABASE gitea;
# CREATE USER 'giteauser'@'localhost' IDENTIFIED BY 'new_password_here';
# GRANT ALL ON gitea.* TO 'giteauser'@'localhost' IDENTIFIED BY 'user_password_here' WITH GRANT OPTION;
# FLUSH PRIVILEGES;
# EXIT;

echo 'Install Gitea...'
adduser --system --shell /bin/bash --comment 'Git Version Control' --user-group --home-dir /home/git -m git
mkdir -p /var/lib/gitea/{custom,data,indexers,public,log}
chown git:git /var/lib/gitea/{data,indexers,log}
chmod 750 /var/lib/gitea/{data,indexers,log}
mkdir /etc/gitea
chown root:git /etc/gitea
chmod 770 /etc/gitea

wget -O /tmp/gitea https://dl.gitea.com/gitea/1.20.5/gitea-1.20.5-linux-amd64
cp /tmp/gitea /usr/local/bin/gitea

# smoke check
#gitea -v

# not sure if needed
#sudo firewall-cmd --add-port 3000/tcp --permanent
#sudo firewall-cmd --reload

echo "Starting Gitea..."
systemctl enable gitea.service
systemctl start gitea.service


echo 'Point your browser at http://YOUR_SERVER_IP:3000/install'

echo "Finished setup.sh OK for provisioning this Gitea node"
echo
