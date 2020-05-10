#!/usr/bin/env bash
# Provisioning script to copy the blackrain application onto the Slackware15-based version 
# This script runs as root on the VM itself
# Files on the Host can be accessed via the /vagrant share

set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning br2020-slack15"

DEST_DIR_ROOT=/home/vagrant/br2020

ROOT_DIR=$PWD

echo $DEST_DIR_ROOT

# Check for patch updates - slows up boot so need a way of avoiding this
# slackpkg update etc. to go in here

echo "Creating directory structure..."
mkdir -p $DEST_DIR_ROOT/app
chown -R vagrant:vagrant $DEST_DIR_ROOT

echo "Copy external packages..."
cp packages/* DEST_DIR_ROOT/packages/*

echo "Copy the br2020 application..."
cp app/*.py DEST_DIR_ROOT/app/*

echo "Copy the br2020 etc configuration..."
cp etc/* DEST_DIR_ROOT/etc/*

echo "Install Python dependencies..."
pip install --upgrade pip
cp installer/REQUIREMENTS.TXT DEST_DIR_ROOT/installer/REQUIREMENTS.TXT
cd DEST_DIR_ROOT/installer
pip install REQUIREMENTS.TXT

echo "Install packages..."
cd ${ROOT_DIR}
pwd
#tree

echo "Finished setup.sh OK for provisioning br2020-slack15"
echo

