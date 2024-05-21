#!/bin/bash

# FIXME : this doesn't seem to be possible in the Packer run - to be investigated

echo "Entered disable_firewall_patch.sh..."

sudo systemctl stop firewalld
sudo systemctl disable firewalld

echo "Exited disable_firewall_patch.sh..."
