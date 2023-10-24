#
# Cookbook Name:: basic
# Recipe:: default
# Author:: Richard Crouch (richard.crouch100@gmail.com)
#
# Copyright (C) 2020 Me, Inc.
# Tools needed during debugging - may not be needed once hpot is stable

# OTHER
# =====

package 'nmap'
package 'whois'
package 'iftop'

log 'Installed debugging tools'

