#!/bin/bash -eux
# FIXME : Can I get the vagrant keys locally off my own web-server
echo "Entered add-vagrant-insecure-key.sh"

USER=vagrant

sudo mkdir -p /home/${USER}/.ssh
sudo chmod 0700 /home/${USER}/.ssh

sudo wget --no-check-certificate \
          https://raw.githubusercontent.com/mitchellh/vagrant/master/keys/vagrant.pub \
          -O /home/${USER}/.ssh/authorized_keys

sudo chmod 0700 /home/${USER}/.ssh
sudo chmod 0600 /home/${USER}/.ssh/authorized_keys
sudo chown -R ${USER} /home/${USER}/.ssh

pwd
sudo tree -a

sudo ls -laF

echo "Exited add-vagrant-insecure-key.sh"
