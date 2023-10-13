#!/usr/bin/env bash
# This script assumes a CentOS host
# Files on the Host can be accessed via the /vagrant share

set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning cloud-init-test node"

# Check for patch updates - slows up boot so need a way of avoiding this
yum update -y --disableplugin=fastestmirror

yum install -y joe cloud-init

# These should be added in the VBOX Packer build in the future
cat >> /etc/hosts <<EOL
# Added during Vagrant run
192.168.1.6  j1900 j1900.ermin.lan
192.168.1.70 chef chef.ermin.com
EOL

cp config/10_datasource.cfg /etc/cloud/cloud.cfg.d/10_datasource.cfg

echo "Finished setup.sh OK for provisioning this node"
echo
