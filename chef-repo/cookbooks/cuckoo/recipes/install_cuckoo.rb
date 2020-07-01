#
# Cookbook:: cuckoo
# Recipe::
#
# Copyright:: 2020, The Authors, All Rights Reserved.

#user 'cuckoo'

# failing at moment
# adduser cuckoo
#execute 'cuckoo_add_to_vagrant' do
#  command 'usermod -a -G vboxusers cuckoo'
#  user 'root'
#end

# this is what it should be
#execute 'install_cuckoo' do
#  command 'pip install -U cuckoo'
#  user 'root'
#end

# install into systemwide
execute 'install_cuckoo' do
  command 'pip install -U cuckoo'
  user 'root'
end
