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

# 777 works - maybe try 744 ?
directory '/app' do
  owner 'crouchr'
  group 'crouchr'
  mode '0777'
  action :create
end

# Store the Blackrain app
directory '/app/src' do
  owner 'crouchr'
  group 'crouchr'
  mode '0777'
  action :create
end

# Store the Blackrain app unit tests
directory '/app/src/tests' do
  owner 'crouchr'
  group 'crouchr'
  mode '0777'
  action :create
end

directory '/app/src/tests/data' do
  owner 'crouchr'
  group 'crouchr'
  mode '0777'
  action :create
end

# Store the GeoIP database
directory '/usr/local/share/GeoIP' do
  owner 'crouchr'
  group 'crouchr'
  mode '0777'
  action :create
end
