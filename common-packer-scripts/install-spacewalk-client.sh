#!/usr/bin/env bash
set -e	# bomb out if any problem

echo "Installing Spacewalk client..."

echo "EARLY EXIT : IGNORE THIS DUE TO BUG"
exit


# Add repos for Spacewalk
sudo yum install -y yum-plugin-tmprepo
sudo yum install -y spacewalk-client-repo --tmprepo=https://copr-be.cloud.fedoraproject.org/results/%40spacewalkproject/spacewalk-2.9-client/epel-7-x86_64/repodata/repomd.xml --nogpg

sudo yum -y install rhn-client-tools rhn-check rhn-setup rhnsd m2crypto yum-rhn-plugin osad rhncfg-actions rhncfg-management
sudo rpm -Uvh http://spacewalk.ermin/pub/rhn-org-trusted-ssl-cert-1.0-1.noarch.rpm

