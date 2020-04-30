#!/bin/bash -eux

USER=jenkins
sudo cp /tmp/jenkins_authorized_keys /home/${USER}/.ssh/authorized_keys
sudo chmod 0700 /home/${USER}/.ssh
sudo chmod 0600 /home/${USER}/.ssh/authorized_keys
sudo chown -R ${USER} /home/${USER}/.ssh

