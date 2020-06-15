# Build the p0f2 container

directory '/usr/local/src/p0f2' do
  owner 'vagrant'
  group 'vagrant'
  mode '0777'
  action :create
end

directory '/usr/local/src/p0f2/dist_files' do
  owner 'vagrant'
  group 'vagrant'
  mode '0777'
  action :create
end

cookbook_file "/usr/local/src/p0f2/Dockerfile" do
  owner 'vagrant'
  group 'vagrant'
  source "p0f2/Dockerfile"
  mode "0644"
end

cookbook_file "/usr/local/src/p0f2/dist_files/p0f2-br-modified.tgz" do
  owner 'vagrant'
  group 'vagrant'
  source "p0f2/dist_files/p0f2-br-modified.tgz"
  mode "0644"
end

execute 'unzip_p0f2_image' do
    cwd '/usr/local/src/p0f2/dist_files'
    user 'root'
    command 'gunzip p0f2-br-modified.tgz'
end

execute 'untar_p0f2_image' do
    cwd '/usr/local/src/p0f2/dist_files'
    user 'root'
    command 'tar xvf p0f2-br-modified.tar'
end

# -B = build unconditionally
execute 'make_p0f2' do
    cwd '/usr/local/src/p0f2/dist_files'
    user 'root'
    command 'make -B'
end
