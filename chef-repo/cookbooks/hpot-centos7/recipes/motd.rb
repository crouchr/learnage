#
# Cookbook:: motd
# Recipe:: default
# ASCII art : http://patorjk.com/software/taag/#p=display&f=Graffiti&t=Type%20Something%20
# Copyright:: 2020, The Authors, All Rights Reserved.

cookbook_file "/etc/motd" do
   source "motd"
   mode "0644"
end
