#!/bin/bash -eux
# Spacewalk - see https://github.com/spacewalkproject/spacewalk/wiki/RegisteringClients

# Add the EPEL repo
sudo yum install -y epel-release

# Add repos for Spacewalk
sudo yum install -y yum-plugin-tmprepo
sudo yum install -y spacewalk-client-repo --tmprepo=https://copr-be.cloud.fedoraproject.org/results/%40spacewalkproject/spacewalk-2.9-client/epel-7-x86_64/repodata/repomd.xml --nogpg

# Update everything
sudo yum update -y
