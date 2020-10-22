#
# Cookbook:: ermin-telegraf
# Recipe:: default
#
# Copyright:: 2020, The Authors, All Rights Reserved.
# Telegraf

directory '/etc/telegraf' do
  owner         'vagrant'
  group         'vagrant'
  mode          '0777'
  action        :create
end

remote_file '/tmp/telegraf-1.15.3-1.x86_64.rpm' do
  source        'https://dl.influxdata.com/telegraf/releases/telegraf-1.15.3-1.x86_64.rpm'
  owner         'root'
  group         'root'
  mode          '0755'
  action        :create
end

yum_package 'install_telegraf' do
    source      '/tmp/telegraf-1.15.3-1.x86_64.rpm'
    action      :install
end

template "/etc/telegraf/telegraf.conf" do
    source      'telegraf.conf.erb'
    mode        '0644'
end

service 'telegraf' do
  action :enable
end

# Temporarily commented out so it works in Docker in Test Kitchen
#service 'telegraf' do
#  action :start
#end

log 'Installed Telegraf'