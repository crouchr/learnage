#!/usr/bin/env bash
echo "Installing Spacewalk client..."

sudo yum -y install rhn-client-tools rhn-check rhn-setup rhnsd m2crypto yum-rhn-plugin osad rhncfg-actions rhncfg-management
sudo rpm -Uvh http://spacewalk.ermin/pub/rhn-org-trusted-ssl-cert-1.0-1.noarch.rpm

