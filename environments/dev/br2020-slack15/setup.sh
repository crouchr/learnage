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
cp /vagrant/etc/rc.d/rc.local /etc/rc.d/rc.local
#cp /vagrant/etc/rc.d/rc.snort /etc/rc.d/rc.snort

#echo "[+] Disable unrequired services..."
#/etc/rc.d/rc.wireless stop
#source /etc/rc.d/rc.bluetooth stop
#chmod -x /etc/rc.d/rc.wireless
#chmod -x /etc/rc.d/rc.bluetooth

# This does not work
#echo "[+] Install Slackware packages..."
#slackpkg install lsof -default_answer=y -batch=on

echo "[+] Install Slackware packages..."
cd $DEST_DIR_ROOT/packages/
rm -f dummy*    # FIXME: in raw box
installpkg *.tgz
installpkg *.txz

echo "[+] Install Python dependencies..."
$PIP install --upgrade pip
$PIP install wheel
cp /vagrant/installer/REQUIREMENTS.TXT $DEST_DIR_ROOT/installer/
cp /vagrant/installer/*.sh $DEST_DIR_ROOT/installer/
cd $DEST_DIR_ROOT/installer
#$PIP install REQUIREMENTS.TXT

# add jenkins user for inspec
echo "Add jenkins user to allow for CI/CD..."
useradd -m -g users -G wheel,floppy,audio,video,cdrom,plugdev,power,netdev,lp,scanner -s /bin/bash jenkins
USER=jenkins
wget --no-check-certificate \
   http://web.ermin/public-keys/jenkins-ermin-keys.pub \
   -O /home/${USER}/.ssh/authorized_keys
chmod 0700 /home/${USER}/.ssh
chmod 0600 /home/${USER}/.ssh/authorized_keys
chown -R ${USER} /home/${USER}/.ssh

# THE END
cd $DEST_DIR_ROOT
tree

cd ${ROOT_DIR}
pwd
#mount

#tree

# update clamav
# update Snort signatures
# update Maldet signatures

echo "Finished setup.sh OK for provisioning br2020-slack15"
echo

#echo "Rebooting..."
#shutdown -r now
