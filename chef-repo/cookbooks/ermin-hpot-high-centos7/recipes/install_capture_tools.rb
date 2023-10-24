#
# Cookbook Name:: basic
# Recipe:: default
# Author:: Richard Crouch (richard.crouch100@gmail.com)
#
# Copyright (C) 2020 Me, Inc.

# Install tools for forensics etc

# OTHER
# =====
package 'p0f'
package 'tcpflow'

log 'Installed capture tools'