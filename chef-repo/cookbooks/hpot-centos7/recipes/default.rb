#
# Cookbook Name:: basic
# Recipe:: default
# Author:: Richard Crouch (richard.crouch100@gmail.com)
#
# Copyright (C) 2020 Me, Inc.

execute 'set_hostname' do
    user 'root'
    command 'hostnamectl set-hostname prd-lon-web1'
end

# Create a temporary folder to hold during build and then delete it
directory '/tmp/hpot-tmp' do
  owner 'vagrant'
  group 'vagrant'
  mode '0777'
  action :create
end

# Fundamental packages
package 'ntp'
package 'joe'

log 'Installed hpot7-centos7 default'
