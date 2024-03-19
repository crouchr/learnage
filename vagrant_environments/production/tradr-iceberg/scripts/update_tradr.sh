#!/bin/bash

echo "Use your Git username (e.g. crouchr & NOT email address) and enter your GIT PAT when prompted for the Password:"
echo "Erasing all prvious installation..."
rm -rf /home/vagrant/iceberg
echo "Pulling in latest codebase into /home/vagrant/iceberg..."
git clone https://github.com/crouchr/iceberg.git /home/vagrant/iceberg
