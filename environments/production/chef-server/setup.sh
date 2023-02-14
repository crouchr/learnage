#!/usr/bin/env bash
# https://docs.chef.io/server/install_server/

set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning this node"
whoami

# Re-enable updates once working
#yum -y update
mkdir -p /home/vagrant/certs

echo 'Install Chef Server...'
cp /vagrant/chef-server-core-12.19.31-1.el7.x86_64.rpm /tmp/
yum -y localinstall /tmp/chef-server-core-12.19.31-1.el7.x86_64.rpm

echo 'Reconfigure Chef Server - runs up the various daemons...'
chef-server-ctl reconfigure

echo 'Create user account...'
chef-server-ctl user-create crouchr Richard Crouch richard.crouch@protonmail.com 'abc123' --filename /home/vagrant/certs/crouchr.pem

#echo 'Create organisation...'
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

echo "Finished setup.sh OK for provisioning this node"
echo
