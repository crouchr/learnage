#!/usr/bin/env bash
# Install Chef Client

USER=vagrant

# Install prerequisites for Chef
sudo yum install -y git

# Install Chef Client - this is latest as of April 2020
sudo curl -L https://www.chef.io/chef/install.sh | sudo bash -s -- -v 15.9.17

sudo mkdir -p /home/${USER}/.chef
sudo chown ${USER}:${USER} /home/${USER}/.chef

sudo mkdir -p /home/${USER}/chef-repo
sudo chown ${USER}:${USER} /home/${USER}/chef-repo

sudo mkdir -p /etc/chef
sudo chown ${USER}:${USER} /etc/chef


