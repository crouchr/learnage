#
# Cookbook:: cuckoo
# Recipe::
#
# Copyright:: 2020, The Authors, All Rights Reserved.

#execute 'add_vbox_repo' do
#    user 'root'
#    command 'echo deb http://download.virtualbox.org/virtualbox/debian xenial contrib | sudo tee -a /etc/apt/sources.list.d/virtualbox.list'
#end

execute 'add_oracle_key_1' do
    user 'root'
    command 'wget -q https://www.virtualbox.org/download/oracle_vbox_2016.asc -O- | sudo apt-key add -'
end

execute 'add_oracle_key_2' do
  user 'root'
  command 'wget -q https://www.virtualbox.org/download/oracle_vbox.asc -O- | sudo apt-key add -'
end

#apt_repository 'add_oracle_repo' do
#  uri "deb http://download.virtualbox.org/virtualbox/debian xenial contrib"
#end
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
