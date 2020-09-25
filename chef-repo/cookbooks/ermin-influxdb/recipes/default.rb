#
# Cookbook:: ermin-influxdb
# Recipe:: default
#
# Copyright:: 2020, The Authors, All Rights Reserved.

# InfluxDB
# cat <<EOF | sudo tee /etc/yum.repos.d/influxdb.repo
# [influxdb]
# name = InfluxDB Repository - RHEL \$releasever
# baseurl = https://repos.influxdata.com/rhel/\$releasever/\$basearch/stable
# enabled = 1
# gpgcheck = 1
# gpgkey = https://repos.influxdata.com/influxdb.key
# EOF
#
# yum -y install influxdb
# mkdir -p /etc/influxdb
# cp /vagrant/influxdb.conf /etc/influxdb/influxdb.conf

directory '/etc/influxdb' do
  owner         'vagrant'
  group         'vagrant'
  mode          '0777'
  action        :create
end

cookbook_file '/etc/yum.repos.d/influxdb.repo' do
  source 'influxdb.repo'
  mode '0755'
  owner 'vagrant'
  group 'vagrant'
end

package 'influxdb'

cookbook_file '/etc/influxdb/influxdb.conf' do
  source 'influxdb.conf'
  mode '0755'
  owner 'vagrant'
  group 'vagrant'
end

service 'influxdb' do
  action :enable
end

service 'influxdb' do
  action :start
end

log 'Installed InfluxDB'
