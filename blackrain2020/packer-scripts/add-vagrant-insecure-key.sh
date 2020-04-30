#!/bin/bash -eux

echo "Entered add-vagrant-insecure-key.sh"

sudo mkdir -p /home/vagrant/.ssh

sudo chmod 0700 /home/vagrant/.ssh

sudo wget --no-check-certificate \
          https://raw.githubusercontent.com/mitchellh/vagrant/master/keys/vagrant.pub \
          -O /home/vagrant/.ssh/authorized_keys

sudo chmod 0700 /home/vagrant/.ssh

sudo chmod 0600 /home/vagrant/.ssh/authorized_keys

sudo chown -R vagrant /home/vagrant/.ssh

pwd
sudo tree -a

sudo ls -laF

echo "Exited add-vagrant-insecure-key.sh"
