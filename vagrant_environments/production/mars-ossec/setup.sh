#!/usr/bin/env bash
# OSSEC Server

set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning this node"

yum update -y --disableplugin=fastestmirror
yum install -y GeoIP-devel
#yum install -y mysql-devel

mkdir -p /var/ossec/etc

echo 'Copy sources...'
cp /vagrant/sources/ossec-hids-2.8.3.tar.gz /tmp/
cp /vagrant/installer/build.sh /tmp/
cp /vagrant/sources/GeoLiteCity.dat /var/ossec/etc/

# Now vagrant ssh into the node
# vagrant ssh
# sudo su -
# cd /tmp
# chmod +x build.sh
# ./build.sh

# server mode
# no email alerting
# no active response
# no syscheck
# no rootkit detection
# no syslog listener
#
# - In order to connect agent and server, you need to add each agent to the server.
#   Run the 'manage_agents' to add or remove them:
#
#   /var/ossec/bin/manage_agents

echo "Finished setup.sh OK for provisioning this node"
echo
