#!/bin/bash -eux
# https://stackoverflow.com/questions/22643177/ssh-onto-vagrant-box-with-different-username

#cut -d: -f1 /etc/passwd

whoami

sudo cat /etc/ssh/sshd_config
df -h
locale -a

#
#echo "Add crouchr to wheel group"
#gpasswd -a crouchr wheel
#

#cut -d: -f1 /etc/passwd

#useradd -m -s /bin/bash -U crouchr -u 666 --groups wheel
#cp -pr /home/vagrant/.ssh /home/crouchr/
#chown -R crouchr:crouchr /home/crouchr
#echo "%crouchr ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/crouchr
