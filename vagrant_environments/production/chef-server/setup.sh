#!/usr/bin/env bash
# https://docs.chef.io/server/install_server/
# Chef uses Nginx, Postgres Dbase, RabbitMQ
# This is a build once script - it does not need to be idempotent and/or robust

set -e	# bomb out if any problem

echo 
echo "[+] Started setup.sh for provisioning this node"
whoami

# Generic =====================================

# Set hostname
hostnamectl set-hostname chef.ermin.lan

# Note : This shouldn't be needed once Chef built with 'new' standard rch-centos7 BOX
#cat >> /etc/hosts <<EOL
## Added during Chef Vagrant run
#192.168.1.5   kube kube.ermin.lan
#192.168.1.6   j1900 j1900.ermin.lan
#192.168.1.56  elk elk.ermin.lan
#192.168.1.70  grafana grafana.ermin.lan
#192.168.1.72  ossec-hpot ossec-hpot.ermin.lan
#192.168.1.73  ossec ossec.ermin.lan
#192.168.1.102 web web.ermin.lan
#192.168.1.109 registry registry.ermin.lan
#EOL
# Note : 192.168.1.71  chef chef.ermin.lan

# Generic =====================================


# Re-enable updates once working...
#yum -y update
mkdir -p /home/vagrant/certs

# 12.19.31 is the final OSS version
echo '[+] Installing Chef Server Core 12.9.31 (final OSS version)...'
cp /vagrant/packages/chef-server-core-12.19.31-1.el7.x86_64.rpm /tmp/
yum -y localinstall /tmp/chef-server-core-12.19.31-1.el7.x86_64.rpm

echo '[+] Configuring Chef Server - runs up the various daemons...'
chef-server-ctl reconfigure

# An RSA private key is generated automatically.
# This is the chef-validator key and should be saved to a safe location.
# The --filename option will save the RSA private key to the specified absolute path.

#echo '[+] Creating Admin user account...'
#chef-server-ctl user-create admin Administrator admin@protonmail.com 'mychefadminpassword' --filename /home/vagrant/certs/admin.pem

#echo '[+] Creating crouchr user account...'
#chef-server-ctl user-create crouchr Richard Crouch richard.crouch@protonmail.com 'mychefpassword' --filename /home/vagrant/certs/crouchr.pem

echo '[+] Creating vagrant user account...'
chef-server-ctl user-create vagrant Vagrant vagrant@protonmail.com 'mychefpassword' --filename /home/vagrant/certs/vagrant.pem

echo '[+] Creating organisation...'
# --filename is where the certs will be written to - shown as 'ermin-org-validator' in Chef Server, as a public key
chef-server-ctl org-create ermin 'ErminOrg' --association_user vagrant --filename /home/vagrant/certs/ermin-org.pem
#chef-server-ctl org-user-add ermin vagrant
#chef-server-ctl org-user-add ermin crouchr

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

# FIXME - fixed IP address - use a variable ?
echo "Chef Server UI Console is ready: http://192.168.1.71 with login: 'crouchr' & password: 'mychefpassword'"

echo "[+] Finished setup.sh OK for provisioning this node"
echo
