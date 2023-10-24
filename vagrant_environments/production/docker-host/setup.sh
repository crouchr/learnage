#!/usr/bin/env bash
set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning this node"

# Check for patch updates - slows up boot so need a way of avoiding this
yum update -y --disableplugin=fastestmirror
systemctl restart sshd

echo "Finished setup.sh OK for provisioning this node"
echo
