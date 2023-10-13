#
# Cookbook:: ermin-grafana
# Recipe:: default
#
# Copyright:: 2020, The Authors, All Rights Reserved.

directory '/etc/grafana' do
  owner         'vagrant'
  group         'vagrant'
  mode          '0777'
  action        :create
end

cookbook_file '/etc/yum.repos.d/grafana.repo' do
  source        'grafana.repo'
  mode          '0755'
  owner         'vagrant'
  group         'vagrant'
end

package 'grafana'

cookbook_file '/etc/grafana/grafana.conf' do
  source        'grafana.conf'
  mode          '0755'
  owner         'vagrant'
  group         'vagrant'
end

service 'grafana' do
  action :enable
end

service 'grafana' do
  action :start
end

log 'Installed Grafana'
