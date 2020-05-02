#!/bin/bash -eux

USER=crouchr

sudo wget --no-check-certificate \
   http://web.ermin/public-keys/rch-nvm-sshkey.pub \
   -O /home/${USER}/.ssh/authorized_keys

#sudo cp /tmp/crouchr_authorized_keys /home/${USER}/.ssh/authorized_keys
sudo chmod 0700 /home/${USER}/.ssh
sudo chmod 0600 /home/${USER}/.ssh/authorized_keys
sudo chown -R ${USER} /home/${USER}/.ssh


