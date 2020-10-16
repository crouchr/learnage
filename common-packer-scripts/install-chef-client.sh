#!/usr/bin/env bash
# Install Chef Client
set -e	# bomb out if any problem

USER=vagrant
CHEF_CLIENT_VERSION=16.1.16

# Install prerequisites for Chef
sudo yum install -y git

# Install Chef Client - this is latest as of April 2020
#sudo curl -L https://www.chef.io/chef/install.sh | sudo bash -s -- -v 15.9.17
sudo curl -L https://www.chef.io/chef/install.sh | sudo bash -s -- -v ${CHEF_CLIENT_VERSION}

sudo mkdir -p /home/${USER}/.chef
sudo chown ${USER}:${USER} /home/${USER}/.chef

sudo mkdir -p /home/${USER}/chef-repo
sudo chown ${USER}:${USER} /home/${USER}/chef-repo

sudo mkdir -p /etc/chef
sudo chown ${USER}:${USER} /etc/chef
