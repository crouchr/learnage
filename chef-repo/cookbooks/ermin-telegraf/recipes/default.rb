#
# Cookbook:: ermin-telegraf
# Recipe:: default
#
# Copyright:: 2020, The Authors, All Rights Reserved.
# Telegraf

#wget https://dl.influxdata.com/telegraf/releases/telegraf-1.15.3-1.x86_64.rpm
#yum -y localinstall telegraf-1.15.3-1.x86_64.rpm
#mkdir -p /etc/telegraf
#cp /vagrant/telegraf.conf /etc/telegraf/telegraf.conf

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
end

template "/etc/telegraf/telegraf.conf" do
    source      'telegraf.conf.erb'
    mode        '0644'
end