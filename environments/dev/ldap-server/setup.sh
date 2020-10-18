#!/usr/bin/env bash
# https://www.itzgeek.com/how-tos/linux/centos-how-tos/step-step-openldap-server-configuration-centos-7-rhel-7.html

set -e	# bomb out if any problem

echo
echo "[+] Started setup.sh for provisioning this node"

echo "[+] Modifying hosts file..."
echo "192.168.1.15 erminserver.ermin erminserver" >> /etc/hosts
echo "192.168.1.2 xps.ermin.com xps" >> /etc/hosts

# Check for patch updates - slows up boot so need a way of avoiding this
yum update -y --disableplugin=fastestmirror

# This will be added to the base Vagrant box in due course
# 'sudo snap install termshark' is all that is needed - https://bugs.launchpad.net/snapd/+bug/1826662
#echo "Installing Snap package manager..."
#sudo yum -y install snapd
#sudo systemctl enable --now snapd.socket
#sudo ln -s /var/lib/snapd/snap /snap
## Wait until seeding has completed
#sudo snap wait system seed.loaded

# Install core LDAP components
yum -y install openldap compat-openldap openldap-clients openldap-servers openldap-servers-sql openldap-devel


echo "[+] Adding PaperTrail destination for rsyslog..."
echo "# The following entry was created during box provisioning" > /etc/rsyslog.d/95-papertrail.conf
echo "*.*          @logs2.papertrailapp.com:52491" >> /etc/rsyslog.d/95-papertrail.conf
systemctl restart rsyslog

# comment out until config is working
echo "[+] Starting OpenLDAP server..."
systemctl start slapd
systemctl enable slapd

echo "Finished setup.sh OK for provisioning this node"
echo
