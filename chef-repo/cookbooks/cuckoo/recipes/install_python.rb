#
# Cookbook:: cuckoo
# Recipe::
#
# Copyright:: 2020, The Authors, All Rights Reserved.

package 'python'
package 'python-dev'
package 'python-virtualenv'
package 'python-setuptools'
package 'python-pip'

execute 'upgrade_pip' do
  cwd '/usr/local/src'
  command 'pip install --upgrade pip'
  user 'root'
end


# has to be installed AFTER swig installed
package 'swig'
execute 'setcap_pcap' do
  command 'pip install m2crypto==0.24.0'
  user 'root'
end