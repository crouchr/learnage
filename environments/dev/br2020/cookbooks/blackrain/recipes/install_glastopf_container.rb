# Build the Glastopf 3.1.3 container

directory '/usr/local/src/glastopf' do
  owner 'crouchr'
  group 'crouchr'
  mode '0777'
  action :create
end

directory '/usr/local/src/glastopf/dist_files' do
  owner 'crouchr'
  group 'crouchr'
  mode '0777'
  action :create
end

cookbook_file "/usr/local/src/glastopf/Dockerfile" do
  source "glastopf/Dockerfile"
  mode "0644"
end

cookbook_file "/usr/local/src/glastopf/dist_files/requirements.txt" do
  source "glastopf/dist_files/requirements.txt"
  mode "0644"
end

cookbook_file "/usr/local/src/glastopf/dist_files/glastopf.cfg" do
  source "glastopf/dist_files/glastopf.cfg"
  mode "0644"
end

# Build the Docker image
execute 'build_glastopf_image' do
    cwd '/usr/local/src/glastopf'
    user 'root'
    command 'docker build -t crouchr:glastopf .'
end

#execute 'tag_glastopf_image' do
#    cwd '/usr/local/src/amun'
#    user 'root'
#    command 'docker tag crouchr/glastopf:v1.0.0'
#end