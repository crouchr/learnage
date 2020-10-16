#!/usr/bin/env bash
set -e	# bomb out if any problem

# first-run.json is stored on the web server so it can be modified rapidly
sudo chef-client -j /home/vagrant/first-run.json
