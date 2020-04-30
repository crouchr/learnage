#!/usr/bin/env bash
# This is lifted from NVM repo

set -o errexit -o nounset -o noglob -o pipefail

echo "_____ SCRIPT_NAME = /centos7_scripts / networking_config _____"

### Sudo changes location between CentOS 6 and CentOS 7 
_SUDO=$(command -v sudo)


# added rch
#"${_SUDO}" systemctl disable NetworkManager.service
#"${_SUDO}" systemctl stop NetworkManager.service


echo "---------------- Testing Networking --------------"
"${_SUDO}" /usr/bin/test -f /etc/sysconfig/network-scripts/ifcfg-eth0 && "${_SUDO}" cat /etc/sysconfig/network-scripts/ifcfg-eth0

"${_SUDO}" /usr/sbin/authconfig --passalgo=sha512 --update

set +e
"${_SUDO}" mkdir -p /root/.rhel/org/
"${_SUDO}" /bin/cp -v /etc/sysconfig/network-scripts/ifcfg-eth0 /root/.rhel/org/ifcfg-eth0_packer 
"${_SUDO}" systemctl list-unit-files --type=service | grep enabled | "${_SUDO}" tee --append /root/.rhel/org/systemctl_service_enabled

echo "---------------- List Running Services  --------------"
"${_SUDO}" cat /root/.rhel/org/systemctl_service_enabled

"${_SUDO}" /usr/bin/test -f /etc/sysconfig/network-scripts/ifcfg-eth0 && "${_SUDO}" sed -i '/HWADDR/d' /etc/sysconfig/network-scripts/ifcfg-eth0
"${_SUDO}" /bin/rm -fv /etc/ssh/ssh_host_dsa* 
set -e

"${_SUDO}" sed -i '/^GRUB\_CMDLINE\_LINUX/s/\"$/\ net\.ifnames\=0\ biosdevname\=0 nousb audit\=1 nofirewire noipv6 noparport selinux\=1"/' /etc/default/grub 
"${_SUDO}" grub2-mkconfig -o /boot/grub2/grub.cfg

set +e
"${_SUDO}" ls -lrth /etc/sysconfig/network-scripts/ifcfg-*
"${_SUDO}" cp /etc/sysconfig/network-scripts/ifcfg-en* /etc/sysconfig/network-scripts/ifcfg-eth0
"${_SUDO}" sed -i 's/DEVICE\=.*/DEVICE\=eth0/g' /etc/sysconfig/network-scripts/ifcfg-eth0
set -e

"${_SUDO}" /usr/bin/test -f /etc/udev/rules.d/70-persistent-net.rules && "${_SUDO}" /bin/rm -fv /etc/udev/rules.d/70-persistent-net.rules 

"${_SUDO}" /usr/bin/test -f /var/lib/dhclient/dhclient-eth0.leases && "${_SUDO}" /bin/rm -fv /var/lib/dhclient/dhclient-eth0.leases 
"${_SUDO}" /usr/bin/test -f /var/lib/dhclient/dhclient--eth0.lease && "${_SUDO}" /bin/rm -fv /var/lib/dhclient/dhclient--eth0.lease  

set +e
echo "---------------- Testing Networking --------------" 
echo "---------- list all network interfaces -----------" 
for _NETWORK in $(ls /etc/sysconfig/network-scripts/ifcfg-* ) ; do ls -l "${_NETWORK}" ; echo "${_NETWORK}" ; cat "${_NETWORK}" ; echo ; done 

"${_SUDO}" /sbin/ip a s
echo "---------- list  -----------"
"${_SUDO}" systemctl status NetworkManager

"${_SUDO}" rpm -qa | grep -i "dkms"

"${_SUDO}" /bin/rm -rfv /tmp/*
set -e
