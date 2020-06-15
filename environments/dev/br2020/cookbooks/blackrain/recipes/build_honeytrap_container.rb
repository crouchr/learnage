# Build the Honeytrap container

ENV['OWNER']='vagrant'
ENV['GROUP']='vagrant'

directory '/usr/local/src/honeytrap' do
  owner $OWNER
  group $GROUP
  mode '0777'
  action :create
end

directory '/usr/local/src/honeytrap/dist_files' do
  owner $OWNER
  group $GROUP
  mode '0777'
  action :create
end

cookbook_file "/usr/local/src/honeytrap/Dockerfile" do
  source "honeytrap/Dockerfile"
  owner $OWNER
  group $GROUP
  mode "0644"
end

cookbook_file "/usr/local/src/honeytrap/dist_files/honeytrap.conf" do
  source "honeytrap/dist_files/honeytrap.conf"
  owner $OWNER
  group $GROUP
  mode "0644"
end

# Build the Docker image
execute 'build_honeytrap_image' do
    cwd '/usr/local/src/honeytrap'
    user 'root'
    command 'docker build -t crouchr:honeytrap .'
end
