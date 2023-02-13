#!/usr/bin/env bash

apt-get update -y -qq > /dev/null
apt-get upgrade -y -qq > /dev/null
apt-get -y -q install linux-headers-$(uname -r) build-essential > /dev/null

wget -P /tmp https://packages.chef.io/stable/ubuntu/14.04/chef-server-core_12.11.1-1_amd64.deb > /dev/null
dpkg -i /tmp/chef-server-core_12.11.1-1_amd64.deb

chown -R vagrant:vagrant /home/vagrant

mkdir /home/vagrant/certs

chef-server-ctl reconfigure
printf "\033c"
chef-server-ctl user-create crouchr Test Lab testlab@testlab.com password --filename /home/vagrant/certs/crouchr.pem
chef-server-ctl org-create crouchchef "Crouch Test Chef Lab" --association_user crouchr --filename /home/vagrant/certs/crouchr.pem
chef-server-ctl install chef-manage
chef-server-ctl reconfigure
chef-manage-ctl reconfigure --accept-license

chef-server-ctl install opscode-reporting
chef-server-ctl reconfigure
opscode-reporting-ctl reconfigure --accept-license


# configure hosts file for our internal network defined by Vagrantfile
cat >> /etc/hosts <<EOL
# vagrant environment nodes
192.168.1.170  chef-server
EOL
#10.0.15.15  lb
#10.0.15.22  web1
#10.0.15.23  web2


printf "\033c"
echo "Chef Console is ready: http://chef-server with login: crouchr password: password"
