#
# Cookbook Name:: basic
# Recipe:: default
# Author:: Richard Crouch (richard.crouch100@gmail.com)
#
# Copyright (C) 2020 Me, Inc.

# Delete the temporary folder used during build
directory '/tmp/hpot-tmp' do
  action :delete
end

# delete logs that indicate the build process
file '/var/log/messages' do
  action :delete
end

# FIXME : delete when tested root account password work
#file '/var/log/secure' do
#  action: delete
#end

# Its obvious this is a VM is a vagrant user is present
#user 'vagrant' do
#  action: remove
#end

execute 'zero_out_1' do
    user 'root'
    command 'dd bs=1M if=/dev/zero of=/var/tmp/zeros || :'
end

execute 'zero_out_1' do
    user 'root'
    command 'rm -f /var/tmp/zeros'
end
