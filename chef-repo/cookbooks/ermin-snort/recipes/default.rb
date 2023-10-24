#
# Cookbook:: ermin-snort
# Recipe:: default
#
# Copyright:: 2023, The Authors, All Rights Reserved.

include_recipe 'ermin-snort::install_snort'
include_recipe 'ermin-snort::configure_snort'
