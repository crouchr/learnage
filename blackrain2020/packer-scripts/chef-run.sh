#!/usr/bin/env bash
# blackrain-first-run.json is stored on the web server so it can be modified rapidly
sudo chef-client -j /home/vagrant/blackrain-first-run.json
