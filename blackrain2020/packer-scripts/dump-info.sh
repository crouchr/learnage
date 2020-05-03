#!/bin/bash -eux
# https://stackoverflow.com/questions/22643177/ssh-onto-vagrant-box-with-different-username

whoami

sudo cat /etc/ssh/sshd_config
df -h
#locale -a

# List all the installed packages
sudo yum list installed
