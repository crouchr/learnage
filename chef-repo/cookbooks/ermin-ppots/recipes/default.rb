#
# Cookbook:: ermin-ppots
# Recipe:: default
#
# Copyright:: 2023, The Authors, All Rights Reserved.
# ppots.com : install basic ppots web-site

remote_directory "/var/www/ppots.com/public_html" do
  source 'html' # <-- this is your directory in files/local_directory
  files_owner 'apache'
  files_group 'apache'
  files_mode '0750'
  action :create
  recursive true
end
