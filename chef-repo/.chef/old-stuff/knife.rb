# See http://docs.chef.io/config_rb_knife.html for more information on knife configuration options

current_dir = File.dirname(__FILE__)
log_level                :info
log_location             STDOUT
node_name                "crouchrermin"
client_key               "#{current_dir}/crouchrermin.pem"
validation_client_name   "blackrainermin-validator"
validation_key           "#{current_dir}/blackrainermin-validator.pem"
chef_server_url          "https://api.chef.io/organizations/blackrainermin"
cookbook_path            ["#{current_dir}/../cookbooks"]
