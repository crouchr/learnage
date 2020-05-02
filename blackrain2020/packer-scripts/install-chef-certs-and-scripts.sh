#!/usr/bin/env bash
# see https://serverfault.com/questions/709820/unattended-chef-client-installation

# config
# ------
sudo wget --no-check-certificate \
   http://web.ermin/private/bootstrap-chef-files/first-run.json \
   -O /home/vagrant/first-run.json

sudo wget --no-check-certificate \
   http://web.ermin/private/bootstrap-chef-files/client.rb \
   -O /etc/chef/client.rb

sudo wget --no-check-certificate \
   http://web.ermin/private/bootstrap-chef-files/knife.rb \
   -O /home/vagrant/.chef/knife.rb

# certs
# -----
sudo wget --no-check-certificate \
   http://web.ermin/private/bootstrap-chef-files/crouchrermin.pem \
   -O /home/vagrant/.chef/crouchrermin.pem

sudo wget --no-check-certificate \
   http://web.ermin/private/bootstrap-chef-files/blackrainermin-validator.pem \
   -O /etc/chef/blackrainermin-validator.pem

sudo wget --no-check-certificate \
   http://web.ermin/private/bootstrap-chef-files/blackrainermin-validator.pem \
   -O /etc/chef/validation.pem

#sudo cp /tmp/crouchrermin.pem /home/vagrant/.chef/crouchrermin.pem
##sudo cp /tmp/erminblackrain-validator.pem /home/vagrant/.chef/erminblackrain-validator.pem
##sudo cp /tmp/blackrainermin-validator.pem /home/vagrant/.chef/blackrainermin-validator.pem
##sudo cp /tmp/chef-server.crt /home/vagrant/.chef/trusted_certs/chef-server.crt
#sudo cp /tmp/blackrainermin-validator.pem /etc/chef/blackrainermin-validator.pem
#sudo cp /tmp/blackrainermin-validator.pem /etc/chef/validation.pem
