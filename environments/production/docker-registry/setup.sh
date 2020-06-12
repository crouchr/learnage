#!/usr/bin/env bash
# https://computingforgeeks.com/install-and-configure-docker-registry-on-centos-7/
# This script is running on the VM itself
# Files on the Host can be accessed via the /vagrant share
#/etc/docker-distribution/registry/config.yml.
set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning this node"

yum -y update

yum install docker-distribution
cp /vagrant/config.yml /etc/docker-distribution/registry/config.yml

echo "Starting Docker Registry..."
systemctl start docker-distribution
systemctl enable docker-distribution

echo "Finished setup.sh OK for provisioning this node"
echo
