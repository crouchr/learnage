#!/usr/bin/env bash
echo "Installing Docker..."

# Install Docker from Docker CE (Stable)
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum -y install docker-ce-19.03.8

# Start Docker
sudo systemctl start docker

# Enable Docker
sudo systemctl enable docker

# Smoke Test - i.e. Packer job will fail if Docker won't basically run
sudo docker version
