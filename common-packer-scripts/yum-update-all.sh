#!/bin/bash -eux
# Spacewalk - see https://github.com/spacewalkproject/spacewalk/wiki/RegisteringClients

# Add the EPEL repo
sudo yum install -y epel-release


# Update everything
sudo yum update -y
