#
# Cookbook:: cuckoo
# Recipe:: default
#
# Copyright:: 2020, The Authors, All Rights Reserved.

execute 'set_hostname' do
    user 'root'
    command 'hostnamectl set-hostname cuckoo'
end

# FIXME : The target system should be able to use local DNS server
execute 'add_web_hosts_file' do
    user 'root'
    command 'echo "192.168.1.102 web.ermin.lan" >> /etc/hosts'
end

apt_update

group 'pcap'

user 'cuckoo' do
  action :remove
  force true
end

user 'cuckoo' do
  comment 'Cuckoo malware user'
  home '/home/cuckoo'
  uid 1999
  manage_home true
end

group 'vboxusers' do
  append true
  members ['cuckoo']
end

group 'pcap' do
  append true
  members ['cuckoo']
end
