# Build the Cowrie container

directory '/usr/local/src/cowrie' do
  owner 'crouchr'
  group 'crouchr'
  mode '0777'
  action :create
end

directory '/usr/local/src/cowrie/dist_files' do
  owner 'crouchr'
  group 'crouchr'
  mode '0777'
  action :create
end

cookbook_file "/usr/local/src/cowrie/Dockerfile" do
  source "cowrie/Dockerfile"
  mode "0644"
end

cookbook_file "/usr/local/src/cowrie/dist_files/cowrie.cfg" do
  source "cowrie/dist_files/cowrie.cfg"
  mode "0644"
end

# Build the Docker image
execute 'build_cowrie_image' do
    cwd '/usr/local/src/cowrie'
    user 'root'
    command 'docker build -t crouchr:cowrie .'
end
