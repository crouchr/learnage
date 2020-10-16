#!/bin/bash -eux
set -e	# bomb out if any problem

USER=jenkins
sudo adduser ${USER}
sudo gpasswd -a ${USER} wheel
sudo mkdir -p /home/${USER}/.ssh
