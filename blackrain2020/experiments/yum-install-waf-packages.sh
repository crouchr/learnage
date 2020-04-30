#!/bin/bash -eux

# Add application-specific packages to make this a WAF

# Apache package installation
sudo yum install -y httpd-2.4.6-90.el7.centos

# mod_ssl package installation
sudo yum install -y mod_ssl-2.4.6-90.el7.centos
