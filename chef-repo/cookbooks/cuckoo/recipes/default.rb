#
# Cookbook:: cuckoo
# Recipe:: default
#
# Copyright:: 2020, The Authors, All Rights Reserved.

execute 'set_hostname' do
    user 'root'
    command 'hostnamectl set-hostname cuckoo'
end

apt_update