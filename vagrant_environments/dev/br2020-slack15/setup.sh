#!/usr/bin/env bash
# Provisioning script to copy the blackrain application onto the Slackware15-based version 
# This script runs as root on the VM itself as part of the vagrant provision step
# Files on the Host can be accessed via the /vagrant share
# The /vagrant share maps to the root i.e. the same dir that the Vagrant file is in

set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning br2020-slack15"

DEST_DIR_ROOT=/opt/br2020
#DEST_DIR_ROOT=/home/vagrant/br2020

ROOT_DIR=$PWD
PIP=pip2

echo $DEST_DIR_ROOT

# Check for patch updates - slows up boot so need a way of avoiding this
# slackpkg update etc. to go in here

echo "[+] Modify hosts file..."
echo "Entry below added by setup.sh provisioning script" >> /etc/hosts
echo "192.168.1.102 web.ermin web" >> /etc/hosts 

# add jenkins user for inspec
USER=jenkins
echo "[+] Add ${USER} user to allow for CI/CD..."
useradd -m -g users -G wheel,floppy,audio,video,cdrom,plugdev,power,netdev,lp,scanner -s /bin/bash ${USER}
mkdir /home/${USER}/.ssh
chown ${USER}:users /home/${USER}/.ssh
chmod 0700 /home/${USER}/.ssh
wget -q --no-check-certificate \
   http://web.ermin/public-keys/rch-nvm-sshkey.pub \
   -O /home/${USER}/.ssh/authorized_keys
chmod 0600 /home/${USER}/.ssh/*
chown ${USER}:users /home/${USER}/.ssh/authorized_keys

# add crouchr user for inspec
USER=crouchr
echo "[+] Add ${USER} user to allow for CI/CD..."
useradd -m -g users -G wheel,floppy,audio,video,cdrom,plugdev,power,netdev,lp,scanner -s /bin/bash ${USER}
mkdir /home/${USER}/.ssh
chown ${USER}:users /home/${USER}/.ssh
chmod 0700 /home/${USER}/.ssh
wget -q --no-check-certificate \
   http://web.ermin/public-keys/rch-nvm-sshkey.pub \
   -O /home/${USER}/.ssh/authorized_keys
chmod 0600 /home/${USER}/.ssh/*
chown ${USER}:users /home/${USER}/.ssh/authorized_keys

echo "[+] Creating directory structure..."
mkdir -p $DEST_DIR_ROOT

mkdir -p $DEST_DIR_ROOT/packages
#chown -R vagrant:users $DEST_DIR_ROOT/packages

mkdir -p $DEST_DIR_ROOT/app
#chown -R vagrant:users $DEST_DIR_ROOT

mkdir -p $DEST_DIR_ROOT/etc
#chown -R vagrant:users $DEST_DIR_ROOT/etc

mkdir -p $DEST_DIR_ROOT/installer
#chown -R vagrant:users $DEST_DIR_ROOT/installer

mkdir -p /etc/snort

mkdir -p /var/run/rchpids
#chown vagrant:users /var/run/rchpids

echo "[+] Copy the Slackware configuration..."
cp /vagrant/etc/motd /etc/motd

echo "[+] Copy Slackware external packages..."
cp /vagrant/packages/*.tgz $DEST_DIR_ROOT/packages/
cp /vagrant/packages/*.txz $DEST_DIR_ROOT/packages/

echo "[+] Override standard configuration..."
cp /vagrant/etc/snort.conf /etc/snort/

echo "[+] Copy the br2020 etc configuration..."
cp /vagrant/etc/snort.conf /etc/snort/

echo "[+] Copy the br2020 application..."
cp /vagrant/app/*.py $DEST_DIR_ROOT/app/

echo "[+] Copy rc.d startup scripts..."
#cp /vagrant/etc/rc.d/rc.local /etc/rc.d/rc.local
#cp /vagrant/etc/rc.d/rc.snort /etc/rc.d/rc.snort

#echo "[+] Disable unrequired services..."
#/etc/rc.d/rc.wireless stop
#source /etc/rc.d/rc.bluetooth stop
#chmod -x /etc/rc.d/rc.wireless
#chmod -x /etc/rc.d/rc.bluetooth

# This does not work
#echo "[+] Install Slackware packages..."
#slackpkg install lsof -default_answer=y -batch=on

#echo "[+] Install Slackware packages..."
#cd $DEST_DIR_ROOT/packages/
#rm -f dummy*    # FIXME: in raw box
#installpkg *.tgz
#installpkg *.txz

echo "[+] Install Python dependencies..."
$PIP install --upgrade pip
$PIP install wheel
cp /vagrant/installer/REQUIREMENTS.TXT $DEST_DIR_ROOT/installer/
cp /vagrant/installer/*.sh $DEST_DIR_ROOT/installer/
cd $DEST_DIR_ROOT/installer
#$PIP install REQUIREMENTS.TXT




# THE END
cd $DEST_DIR_ROOT
tree

cd ${ROOT_DIR}
pwd

cat /etc/group
cat /etc/shadow
ifconfig
#mount

#tree

# update clamav
# update Snort signatures
# update Maldet signatures

echo "Finished setup.sh OK for provisioning br2020-slack15"
echo

#echo "Rebooting..."
#shutdown -r now
