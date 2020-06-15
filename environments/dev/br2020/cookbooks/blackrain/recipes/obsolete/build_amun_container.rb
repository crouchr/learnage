# Build the Glastopf 3.1.3 container

directory '/usr/local/src/amun' do
  owner 'crouchr'
  group 'crouchr'
  mode '0777'
  action :create
end

directory '/usr/local/src/amun/dist_files' do
  owner 'crouchr'
  group 'crouchr'
  mode '0777'
  action :create
end

cookbook_file "/usr/local/src/amun/Dockerfile" do
  source "amun/Dockerfile"
  mode "0644"
end

cookbook_file "/usr/local/src/amun/dist_files/amun.conf" do
  source "amun/dist_files/amun.conf"
  mode "0644"
end

# Build the Docker image
execute 'build_amun_image' do
    cwd '/usr/local/src/amun'
    user 'root'
    command 'docker build -t crouchr:amun .'
end

