#
# Cookbook:: vcc-basic
# Recipe:: install_packages
#
# Copyright:: 2023, The Authors, All Rights Reserved.

cookbook_file '/usr/local/bin/networks_regex_tool.py' do
  source 'networks_regex_tool.py'
  mode '0755'
  Chef::Log.info "install_packages : install networks_regex_tool"
end
