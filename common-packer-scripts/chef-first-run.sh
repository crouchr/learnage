#!/usr/bin/env bash
# first-run.json is stored on the web server so it can be modified rapidly
sudo chef-client -j /home/vagrant/first-run.json
