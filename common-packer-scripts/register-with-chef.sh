#!/usr/bin/env bash
# Bootstrap the node into Chef and install ntp
#sudo chef-client -j /home/vagrant/first-run.json --chef-license accept

# Running with no run list will register the node to Chef
sudo chef-client --chef-license accept
