#!/usr/bin/env bash
echo "Installing Docker..."

# Install packages
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce
sudo yum install -y docker-ce-cli
sudo yum install -y containerd.io
sudo yum install -y docker-compose

# Allow vagrant user to run docker
sudo usermod -aG docker vagrant

# Start Docker
sudo systemctl start docker

# Enable Docker
sudo systemctl enable docker

