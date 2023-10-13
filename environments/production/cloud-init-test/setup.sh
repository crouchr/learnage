#!/usr/bin/env bash
# This script assumes a CentOS host
# Files on the Host can be accessed via the /vagrant share

set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning squid node"

# Check for patch updates - slows up boot so need a way of avoiding this
yum update -y --disableplugin=fastestmirror

yum install -y joe cloud-init

echo "Finished setup.sh OK for provisioning this squid node"
echo
