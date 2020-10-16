#!/usr/bin/env bash
# https://hostpresto.com/community/tutorials/how-to-install-clamav-on-centos-7/
set -e	# bomb out if any problem

echo "Installing ClamAV..."
sudo yum -y install clamav-server clamav-data clamav-update clamav-filesystem
sudo yum -y install clamav clamav-scanner-systemd clamav-devel clamav-lib clamav-server-system
