#
# Cookbook:: cuckoo
# Recipe::
#
# Copyright:: 2020, The Authors, All Rights Reserved.

execute 'install_cuckoo' do
  command 'pip install -U cuckoo'
  user 'root'
end

execute 'install_vmcloak' do
  command 'pip install -U vmcloak'
  user 'root'
end