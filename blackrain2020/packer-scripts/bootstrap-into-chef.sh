#!/usr/bin/env bash
# Bootstrap the node into Chef and install ntp
sudo chef-client -j /home/vagrant/blackrain-first-run.json --chef-license accept
