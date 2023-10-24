#
# Cookbook:: emrin-motd-br
# Recipe:: default
#
# Copyright:: 2020, The Authors, All Rights Reserved.

cookbook_file "/etc/motd" do
   source "motd"
   mode "0644"
end
