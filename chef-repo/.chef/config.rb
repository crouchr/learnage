# See https://docs.chef.io/workstation/config_rb/ for more information on knife
# This file was originally exported from Chef Server
# current_dir is chef-repo/.chef

current_dir = File.dirname(__FILE__)
log_level                :info
log_location             STDOUT
node_name                "crouchr"
client_key               "#{current_dir}/crouchr.pem"
chef_server_url          "https://chef/organizations/ermin"
cookbook_path            ["#{current_dir}/../cookbooks"]

