#!/bin/bash -eux
# Ref : https://github.com/gwagner/packer-centos/blob/master/provisioners/install-vmware-guest-additions.sh
# whole script needs to be looked at - contain stuff from vbox guest additions
# Mount Disk Image
cd /tmp
sudo mkdir /tmp/isomount

sudo cd /root
sudo ls -laF

sudo cd /home/vagrant
sudo ls -laF


#sudo mount -t iso9660 -o loop /root/VBoxGuestAdditions.iso /tmp/isomount
sudo mount -t iso9660 -o loop /home/vagrant/VBoxGuestAdditions.iso /tmp/isomount
#
## Install the drivers
sudo /tmp/isomount/VBoxLinuxAdditions.run --nox11
#
## Clean Up
sudo umount isomount
#sudo rm -rf isomount /root/VBoxGuestAdditions.iso
sudo rm -rf isomount /home/vagrant/VBoxGuestAdditions.iso

# VMware
#sudo mount -t iso9660 -o loop /root/linux.iso /tmp/isomount
#
## Install the drivers
#cp /tmp/isomount/VMwareTools-*.gz /tmp
#tar -zxvf VMwareTools*.gz
#./vmware-tools-distrib/vmware-install.pl -d
#
## Cleanup
#sudo umount isomount
#sudo rm -rf isomount /root/linux.iso VMwareTools*.gz vmware-tools-distrib
