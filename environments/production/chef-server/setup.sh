#!/usr/bin/env bash
# https://docs.chef.io/server/install_server/
# Chef uses Nginx, Postgres Dbase, RabbitMQ

set -e	# bomb out if any problem

echo 
echo "[+] Started setup.sh for provisioning this node"
whoami

# Re-enable updates once working...
#yum -y update
mkdir -p /home/vagrant/certs

echo '[+] Installing Chef Server...'
cp /vagrant/chef-server-core-12.19.31-1.el7.x86_64.rpm /tmp/
yum -y localinstall /tmp/chef-server-core-12.19.31-1.el7.x86_64.rpm

echo '[+] Configuring Chef Server - runs up the various daemons...'
chef-server-ctl reconfigure

# An RSA private key is generated automatically.
# This is the chef-validator key and should be saved to a safe location.
# The --filename option will save the RSA private key to the specified absolute path.
echo '[+] Creating user account...'
chef-server-ctl user-create crouchr Richard Crouch richard.crouch@protonmail.com 'abc123' --filename /home/vagrant/certs/crouchr.pem

echo '[+] Creating organisation...'
# --filename is where the certs will be written to
chef-server-ctl org-create br2023 'BlackRain2023' --association_user crouchr --filename /home/vagrant/certs/br2023.pem
chef-server-ctl install chef-manage
chef-server-ctl reconfigure
chef-manage-ctl reconfigure

# Telegraf
#wget -P /tmp https://dl.influxdata.com/telegraf/releases/telegraf-1.8.3-1.x86_64.rpm
#yum -y /tmp/localinstall telegraf-1.8.3-1.x86_64.rpm
#cp /vagrant/telegraf.conf /etc/telegraf/telegraf.conf
#echo "Starting Telegraf Agent..."
#systemctl enable telegraf
#systemctl start telegraf

echo "[+] Finished setup.sh OK for provisioning this node"
echo
