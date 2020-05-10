#!/usr/bin/env bash
# Experimental
# Delete ourselves from the Chef Server
echo "De-register from Chef"

sudo rm -f /etc/chef/client.pem
sudo knife client delete rch-centos7 --yes


