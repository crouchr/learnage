#
# Cookbook Name:: basic
# Recipe:: default
# Author:: Richard Crouch (richard.crouch100@gmail.com)
#
# Copyright (C) 2020 Me, Inc.

execute 'set_hostname' do
    user 'root'
    command 'hostnamectl set-hostname br2020'
end

directory '/opt/br2020' do
  owner 'crouchr'
  group 'crouchr'
  mode '0755'
  action :create
end

#directory '/opt/br2020/app' do
#  owner 'vagrant'
#  group 'vagrant'
#  mode '0755'
#  action :create
#end