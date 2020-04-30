#!/bin/bash -eux
# https://stackoverflow.com/questions/22643177/ssh-onto-vagrant-box-with-different-username

#cut -d: -f1 /etc/passwd

#whoami

sudo cat /etc/ssh/sshd_config
df -h

echo "List the installed locales"
locale -a

# List all the installed packages
sudo yum list installed

# FIXME : got 'command not found' on this
#echo "Show if IPv6 disabled"
#ip a | grep inet6
