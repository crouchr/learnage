#
# Cookbook:: vcc-basic
# Recipe:: default
#
# Copyright:: 2023, The Authors, All Rights Reserved.

directory '/etc/httpd' do
  recursive true
end

template '/etc/httpd/test-apache.conf' do
  source 'apache.conf.erb'
  variables(
    admin_page_ips: node['WAF']['admin_page_ips']
  )
  owner 'root'
  group 'root'
  mode '0644'
end