#!/usr/bin/env bash
# https://docs.chef.io/server/install_server/

set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning this node"
whoami

# Re-enable updates once working
#yum -y update
mkdir -p /home/vagrant/certs

#echo "Install Chef Server 15"
#wget -P /tmp http://192.168.1.102/centos7-packages/chef-server-core-15.5.1-1.el7.x86_64.rpm
#yum -y localinstall /tmp/chef-server-core-15.5.1-1.el7.x86_64.rpm
#chef-server-ctl reconfigure accept --chef-license
#chef-server-ctl reconfigure
#chef-server-ctl user-create crouchr Richard Crouch richard.crouc@protonmail.com 'abc123' --filename /home/vagrant/certs/crouchr.pem

echo 'Install Chef Server...'
cp /vagrant/chef-server-core-12.19.31-1.el7.x86_64.rpm /tmp/
yum -y localinstall /tmp/chef-server-core-12.19.31-1.el7.x86_64.rpm
#curl -L https://omnitruck.cinc.sh/install.sh | sudo bash -s -- -P cinc-server -v 14
#curl -L https://omnitruck.cinc.sh/install.sh | sudo bash -s -- -P cinc-server -v 16
# works this far

#echo 'Reconfigure Chef Server - runs up the various daemons...'
#chef-server-ctl reconfigure
# crashes here

#echo 'Create user account...'
#chef-server-ctl user-create crouchr Richard Crouch richard.crouch@protonmail.com 'abc123' --filename /home/vagrant/certs/crouchr.pem

#echo 'Create organisation...'
#chef-server-ctl org-create br2023 'BlackRain2023' --association_user crouchr --filename /home/vagrant/certs/br2023.pem

# Telegraf
#wget -P /tmp https://dl.influxdata.com/telegraf/releases/telegraf-1.8.3-1.x86_64.rpm
#yum -y /tmp/localinstall telegraf-1.8.3-1.x86_64.rpm
#cp /vagrant/telegraf.conf /etc/telegraf/telegraf.conf
#echo "Starting Telegraf Agent..."
#systemctl enable telegraf
#systemctl start telegraf

echo "Finished setup.sh OK for provisioning this node"
echo
