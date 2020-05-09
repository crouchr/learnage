#!/bin/bash -eux
# https://stackoverflow.com/questions/22643177/ssh-onto-vagrant-box-with-different-username

whoami

sudo cat /etc/ssh/sshd_config
df -h

# Show all files
echo "==================================================="
sudo tree /etc/chef
echo "==================================================="
sudo tree /home/vagrant
echo "==================================================="

# List all the installed packages
sudo yum list installed