#
# Cookbook Name:: basic
# Recipe:: default
# Author:: Richard Crouch (richard.crouch100@gmail.com)
#
# Copyright (C) 2020 Me, Inc.

# Install packages to be exploited by attackers

# OTHER
# =====
package 'telnet-server'
package 'telnet'

# Start TelnetD
service 'telnet.socket' do
  action :restart
end

# Enable TelnetD
service 'telnet.socket' do
  action :enable
end

log 'Installed honeypot services'
