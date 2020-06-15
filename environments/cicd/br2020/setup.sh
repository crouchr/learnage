#!/usr/bin/env bash
# This script is running on the VM itself
# Files on the Host can be accessed via the /vagrant share

set -e	# bomb out if any problem

echo
echo "Started setup.sh for provisioning this node"

cd /vagrant
ls -laF

echo "Finished setup.sh for provisioning this node"
