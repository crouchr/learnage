#!/usr/bin/env bash
# This script is running on the VM itself
# Files on the Host can be accessed via the /vagrant share

set -e	# bomb out if any problem

echo
echo 'Started setup.sh for provisioning this node'

#cd /
#tree

echo 'contents of project root /vagrant'
cd /vagrant
ls -laF
cat dns.json

echo 'contents of dev chef folder'
cd /vagrant/chef
ls -laF

echo 'contents of learnage folder'
cd /vagrant/learnage/chef-repo/.chef/
ls -laF
cat solo.rb


cd /vagrant/chef

echo 'Finished setup.sh for provisioning this node'
