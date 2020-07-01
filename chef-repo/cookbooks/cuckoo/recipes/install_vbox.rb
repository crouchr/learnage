#
# Cookbook:: cuckoo
# Recipe::
#
# Copyright:: 2020, The Authors, All Rights Reserved.

execute 'add_oracle_key_1' do
    user 'root'
    command 'wget -q https://www.virtualbox.org/download/oracle_vbox_2016.asc -O- | sudo apt-key add -'
end

execute 'add_oracle_key_2' do
  user 'root'
  command 'wget -q https://www.virtualbox.org/download/oracle_vbox.asc -O- | sudo apt-key add -'
end

execute 'add_oracle_repo' do
  user 'root'
  command 'echo "deb http://download.virtualbox.org/virtualbox/debian xenial contrib" >> /etc/apt/sources.list'
end

execute 'apt-get_update' do
  user 'root'
  command 'apt-get update'
end

execute 'install_vbox5' do
    user 'root'
    command 'apt-get -y install virtualbox-5.2'
end
