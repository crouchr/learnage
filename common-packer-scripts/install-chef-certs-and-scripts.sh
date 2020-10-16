#!/usr/bin/env bash
# see https://serverfault.com/questions/709820/unattended-chef-client-installation
set -e	# bomb out if any problem

# config
# ------
sudo wget --no-check-certificate \
   http://web.ermin.com/private/bootstrap-chef-files/client.rb \
   -O /etc/chef/client.rb

sudo wget --no-check-certificate \
   http://web.ermin.com/private/bootstrap-chef-files/validation.pem \
   -O /etc/chef/validation.pem

sudo wget --no-check-certificate \
   http://web.ermin.com/private/bootstrap-chef-files/knife.rb \
   -O /home/vagrant/.chef/knife.rb

sudo wget --no-check-certificate \
   http://web.ermin.com/private/bootstrap-chef-files/first-run.json \
   -O /home/vagrant/first-run.json

sudo wget --no-check-certificate \
   http://web.ermin.com/private/bootstrap-chef-files/knife.rb \
   -O /home/vagrant/.chef/knife.rb

# certs
# -----
sudo wget --no-check-certificate \
   http://web.ermin.com/private/bootstrap-chef-files/crouchrermin.pem \
   -O /home/vagrant/.chef/crouchrermin.pem

sudo wget --no-check-certificate \
   http://web.ermin.com/private/bootstrap-chef-files/blackrainermin-validator.pem \
   -O /home/vagrant/.chef/blackrainermin-validator.pem
