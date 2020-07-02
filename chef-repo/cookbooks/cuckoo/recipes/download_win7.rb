# Recipe:: default
#
# Copyright:: 2020, The Authors, All Rights Reserved.

# Pull the Windows7 ISO from web.ermin.lab
remote_file '/tmp/win7ultimate.iso' do
  source 'http://web.ermin.lan/isos/win7ultimate.iso'
  owner 'cuckoo'
  group 'cuckoo'
  mode '0755'
  action :create
end

directory '/mnt/win7' do
  owner 'root'
  group 'root'
  mode '0755'
  action :create
end

execute 'mount_win7_iso' do
  command 'mount -o ro,loop /tmp/win7ultimate.iso /mnt/win7'
  user 'root'
end
