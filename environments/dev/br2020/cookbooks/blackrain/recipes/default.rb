#
# Cookbook Name:: basic
# Recipe:: default
# Author:: Richard Crouch (richard.crouch100@gmail.com)
#
# Copyright (C) 2020 Me, Inc.

execute 'set_hostname' do
    user 'root'
    command 'hostnamectl set-hostname br2020'
end

# Set default route as via Internet
execute 'del_default_route' do
    user 'root'
    command 'route del default'
end

execute 'add_default_route' do
    user 'root'
    command 'route add default gw 192.168.1.1'
end

execute 'show_route_table' do
    user 'root'
    command 'route -n'
end

# Misc global scripts e.g. starting honeypots etc
directory '/opt/br2020' do
  owner 'vagrant'
  group 'vagrant'
  mode '0777'
  action :create
end

# Misc global scripts e.g. starting honeypots etc
directory '/opt/br2020/bin' do
  owner 'vagrant'
  group 'vagrant'
  mode '0777'
  action :create
end

# Global configuration
directory '/opt/br2020/etc' do
  owner 'vagrant'
  group 'vagrant'
  mode '0777'
  action :create
end

# 777 works - maybe try 744 ?
directory '/app' do
  owner 'vagrant'
  group 'vagrant'
  mode '0777'
  action :create
end

# Store the Blackrain app
directory '/app/src' do
  owner 'vagrant'
  group 'vagrant'
  mode '0777'
  action :create
end

# Store the Blackrain app unit tests
directory '/app/src/tests' do
  owner 'vagrant'
  group 'vagrant'
  mode '0777'
  action :create
end

directory '/app/src/tests/data' do
  owner 'vagrant'
  group 'vagrant'
  mode '0777'
  action :create
end

# Store the GeoIP database
directory '/usr/local/share/GeoIP' do
  owner 'vagrant'
  group 'vagrant'
  mode '0777'
  action :create
end

# These mounts are where the logs in the docker honeypots will be sent
directory '/data' do
  owner 'vagrant'
  group 'vagrant'
  mode '0777'
  action :create
end

# Honeytrap
directory '/data/honeytrap' do
  owner 'vagrant'
  group 'vagrant'
  mode '0777'
  action :create
end

# See Virtual Honeypots book p200 : Queue all new incoming requests for use by Honeytrap
execute 'mod_iptables_honeytrap' do
    user 'root'
    command 'iptables -A INPUT -i enp0s8 -p tcp --syn -m state --state NEW -j QUEUE'
end

# AMUN
directory '/data/amun' do
  owner 'vagrant'
  group 'vagrant'
  mode '0777'
  action :create
end

# Glastopf
directory '/data/glastopf' do
  owner 'vagrant'
  group 'vagrant'
  mode '0777'
  action :create
end

# Dionaea
directory '/data/dionaea' do
  owner 'vagrant'
  group 'vagrant'
  mode '0777'
  action :create
end

execute 'chown_dionaea' do
    user 'root'
    command 'chown -R vagrant:vagrant dionaea'
end

execute 'chmod_dionaea' do
    user 'root'
    command 'chmod 777 -R dionaea'
end

# Cowrie
directory '/data/cowrie' do
  owner 'vagrant'
  group 'vagrant'
  mode '0777'
  action :create
end

# p0f2
directory '/data/p0f' do
  owner 'vagrant'
  group 'vagrant'
  mode '0777'
  action :create
end
