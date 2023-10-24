#
# Cookbook Name:: basic
# Recipe:: default
# Author:: Richard Crouch (richard.crouch100@gmail.com)
#
# Copyright (C) 2023 Me, Inc.

include_recipe 'ermin-hpot-high-centos7::base'
include_recipe 'ermin-hpot-high-centos7::create_my_user'
include_recipe 'ermin-hpot-high-centos7::create_fake_users'
include_recipe 'ermin-hpot-high-centos7::install_keylogger'
include_recipe 'ermin-hpot-high-centos7::install_hpot_services'
include_recipe 'ermin-hpot-high-centos7::install_httpd'
include_recipe 'ermin-hpot-high-centos7::install_waf'

# issues with web-server ? hostname resolution ?
#include_recipe 'ermin-hpot-high-centos7::install_ppots'
#include_recipe 'ermin-hpot-high-centos7::install_web_vulns'

log 'Ran default'
