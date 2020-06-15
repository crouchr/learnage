#!/usr/bin/env bash
# This script is running on the VM itself
# Files on the Host can be accessed via the /vagrant share

set -e	# bomb out if any problem

echo
echo 'Started setup.sh for provisioning this node'

#cd /
#tree

echo 'Contents of project root /vagrant'
cd /vagrant
ls -laF
cat dna.json

echo 'Chef recipes (development)'
cd /vagrant/learnage/environments/dev/br2020/cookbooks/blackrain/recipes/default.rb
ls -laF

echo 'Contents of learnage folder'
cd /vagrant/learnage/chef-repo/.chef/
ls -laF
cat solo.rb


cd /vagrant/chef

echo 'Finished setup.sh for provisioning this node'
