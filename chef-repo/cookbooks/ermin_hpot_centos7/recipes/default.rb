#
# Cookbook Name:: basic
# Recipe:: default
# Author:: Richard Crouch (richard.crouch100@gmail.com)
#
# Copyright (C) 2020 Me, Inc.

execute 'set_hostname' do
    user 'root'
    command 'hostnamectl set-hostname dev-lon-web1'
end

# Create a temporary folder to hold during build and then delete it
directory '/tmp/hpot-tmp' do
  owner 'vagrant'
  group 'vagrant'
  mode '0777'
  action :create
end

# Fundamental packages for managing the node - assuming target node is CentOS7 AMI
# This is the same list as install-tools-packages.sh
package 'yum-utils'
package 'ntp'
package 'htop'
package 'tcpdump'
package 'traceroute'
package 'tcpflow'
package 'bind-utils'
package 'joe'
package 'shadow-utils'
package 'tree'
package 'ncdu'
package 'wireshark'

user 'root' do
  password 'idltbbtss'
end

log 'Installed hpot7-centos7 default'
