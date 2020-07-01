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

group 'pcap'
user 'cuckoo'

# failing at moment
#execute 'cuckoo_add_to_vagrant' do
#  command 'usermod -a -G vboxusers cuckoo'
#  user 'root'
#end

group 'vboxusers' do
  append true
  members ['cuckoo']
end

group 'pcap' do
  append true
  members ['cuckoo']
end
