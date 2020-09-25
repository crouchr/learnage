#
# Cookbook:: METMINI
# Recipe:: default
# Environment Cookbook
#
# Copyright:: 2020, The Authors, All Rights Reserved.

#include_recipe 'ermin_telegraf_agent' if node['ERMIN']['feature']['METMINI']['enable_telegraf']

include_recipe 'ermin-centos7'
include_recipe 'ermin-python3'
include_recipe 'ermin-mariadb'
include_recipe 'ermin-telegraf'