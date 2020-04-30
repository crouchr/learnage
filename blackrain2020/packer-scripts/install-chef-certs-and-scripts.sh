#!/usr/bin/env bash
# see https://serverfault.com/questions/709820/unattended-chef-client-installation

# config
# ------
sudo cp /tmp/first-run.json /home/vagrant/first-run.json
sudo cp /tmp/client.rb /etc/chef/client.rb
sudo cp /tmp/knife.rb  /home/vagrant/.chef/knife.rb

# certs
# -----
sudo cp /tmp/crouchrermin.pem /home/vagrant/.chef/crouchrermin.pem
#sudo cp /tmp/erminblackrain-validator.pem /home/vagrant/.chef/erminblackrain-validator.pem
#sudo cp /tmp/blackrainermin-validator.pem /home/vagrant/.chef/blackrainermin-validator.pem
#sudo cp /tmp/chef-server.crt /home/vagrant/.chef/trusted_certs/chef-server.crt
sudo cp /tmp/blackrainermin-validator.pem /etc/chef/blackrainermin-validator.pem
sudo cp /tmp/blackrainermin-validator.pem /etc/chef/validation.pem


# scripts
# -------
#sudo cp /tmp/bootstrap-blackrain.sh /home/vagrant/bootstrap-blackrain.sh
#sudo chmod +x /home/vagrant/bootstrap-blackrain.sh
#sudo chown vagrant:vagrant /home/vagrant/bootstrap-blackrain.sh
