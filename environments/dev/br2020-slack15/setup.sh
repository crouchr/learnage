#!/usr/bin/env bash
# Provisioning script to copy the blackrain application onto the Slackware15-based version 
# This script runs as root on the VM itself as part of the vagrant provision step
# Files on the Host can be accessed via the /vagrant share

set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning br2020-slack15"

DEST_DIR_ROOT=/home/vagrant/br2020

ROOT_DIR=$PWD

echo $DEST_DIR_ROOT

# Check for patch updates - slows up boot so need a way of avoiding this
# slackpkg update etc. to go in here

echo "Creating directory structure"
echo "============================"
mkdir -p $DEST_DIR_ROOT/app
chown -R vagrant:vagrant $DEST_DIR_ROOT

mkdir -p /var/run/rchpids
chown vagrant:vagrant /var/run/rchpids

echo "Copy external packages"
echo "======================"
cp packages/* DEST_DIR_ROOT/packages/*

echo "Copy the br2020 application"
echo "==========================="
cp app/*.py DEST_DIR_ROOT/app/*

echo "Copy the br2020 etc configuration"
echo "================================="
cp etc/* DEST_DIR_ROOT/etc/*

echo "Install Python dependencies"
echo "==========================="
pip install --upgrade pip
cp installer/REQUIREMENTS.TXT DEST_DIR_ROOT/installer/REQUIREMENTS.TXT
cd DEST_DIR_ROOT/installer
pip install REQUIREMENTS.TXT

echo "Install pre-compiled packages"
echo "============================="
cd ${ROOT_DIR}
pwd
#tree

# update clamav
# update Snort signatures
# update Maldet signatures

echo "Finished setup.sh OK for provisioning br2020-slack15"
echo
