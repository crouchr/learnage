#
# Cookbook:: vcc-basic
# Recipe:: default
#
# Copyright:: 2023, The Authors, All Rights Reserved.

directory '/etc/httpd' do
  recursive true
end

#all_admin_ips = node['WAF']['admin_page_ips']
all_admin_ips = node['WAF']['admin_page_ips'] + node['WAF']['additional_admin_page_ips']

template '/etc/httpd/test-apache.conf' do
  source 'apache.conf.erb'
  variables(
    #admin_page_ips: node['WAF']['admin_page_ips']
    admin_page_ips: all_admin_ips
  )
  owner 'root'
  group 'root'
  mode '0644'
end