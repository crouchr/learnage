chef_repo = File.join(File.dirname(__FILE__), "..")

chef_server_url "http://127.0.0.1:9501"
node_name 	"volker-dev"
client_key File.join(File.dirname(__FILE__), "volker-dev.pem")
cookbook_path 	"#{chef_repo}/cookbooks"
cache_type 	"BasicFile"
cache_options 	:path => "#{chef_repo}/checksums"
