#!/bin/bash -eux
set -e	# bomb out if any problem

# Install pre-requisite packages for VBox Guest Additions
sudo yum install -y kernel-devel-$(uname -r) kernel-headers-$(uname -r) gcc make perl
sudo yum install -y binutils patch libgomp glibc-headers glibc-devel bzip2

# Install dkms - needs epel
sudo yum install -y dkms

# Not in standard installer
sudo yum install -y wget
