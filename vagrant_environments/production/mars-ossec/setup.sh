#!/usr/bin/env bash
# OSSEC Server

set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning this node"

yum update -y --disableplugin=fastestmirror

echo 'Copy sources...'
cp /vagrant/sources/ossec-hids-3.7.0.tar.gz /tmp/
tar xvf /tmp/ossec-hids-3.7.0.tar.gz

# sudo su -
# cd /tmp



# server mode
# no email alerting
# no active response
# no syscheck - until production ready
# no rootkit detection - until production ready
# no logging to udp 514 - i.e. only use encrypted channel via agents


# /tmp/ossec-hids-2.9.3/install.sh
#
# - In order to connect agent and server, you need to add each agent to the server.
#   Run the 'manage_agents' to add or remove them:
#
#   /var/ossec/bin/manage_agents

echo "Finished setup.sh OK for provisioning this node"
echo
