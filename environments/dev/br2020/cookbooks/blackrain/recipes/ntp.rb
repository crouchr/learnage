#
# Cookbook Name:: blackrain
# Recipe:: ntp
# Author:: Richard Crouch (richard.crouch100@gmail.com)
#
# Copyright (C) 2020 Me, Inc.
# Needs some configuration file to be present
package 'ntp'

service 'ntp' do
  action :start
end
