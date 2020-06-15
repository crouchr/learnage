#!/usr/bin/env bash
# This script is running on the VM itself
# Files on the Host can be accessed via the /vagrant share

set -e	# bomb out if any problem

echo
echo "Started setup.sh for provisioning this node"

#cd /
#tree

#echo "contents of project root"
#cd /vagrant
#ls -laF

#echo "contents of dev chef folder"
#cd /vagrant/chef
#ls -laF

cd /vagrant/chef



echo "Finished setup.sh for provisioning this node"
