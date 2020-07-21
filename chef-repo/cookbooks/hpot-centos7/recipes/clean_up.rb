#
# Cookbook Name:: basic
# Recipe:: default
# Author:: Richard Crouch (richard.crouch100@gmail.com)
#
# Copyright (C) 2020 Me, Inc.

# Create a temporary folder to hold during build and then delete it
directory '/tmp/hpot-tmp' do
  action :delete
end

execute 'zero_out_1' do
    user 'root'
    command 'dd bs=1M if=/dev/zero of=/var/tmp/zeros || :'
end

execute 'zero_out_1' do
    user 'root'
    command 'rm -f /var/tmp/zeros'
end

log 'Clean up'
