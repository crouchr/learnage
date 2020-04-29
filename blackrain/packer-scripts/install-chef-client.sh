#!/usr/bin/env bash
# Install Chef Client

# Install prerequisites for Chef
sudo yum install -y git

# Install Chef Client - this is latest as of April 2020
sudo curl -L https://www.chef.io/chef/install.sh | sudo bash -s -- -v 15.9.17

sudo mkdir -p /home/vagrant/.chef
sudo mkdir -p /etc/chef
sudo chown vagrant:vagrant /etc/chef

#sudo mkdir -p /home/vagrant/.chef/trusted_certs


