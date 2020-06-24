# Not always reliable ?
# Unreliable at moment so commented out temporarily
# https://download.docker.com/linux/centos/7/x86_64/stable/Packages/ - contains rpms - todo - use the rpms
# Not needed as Docker now built into the rch-centos7-docker box image

execute 'add_docker_repo' do
    cwd '/usr/local/src'
    user 'root'
    command 'yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo'
end

execute 'install_docker' do
    cwd '/usr/local/src'
    user 'root'
    command 'yum install -y docker-ce'
end

execute 'install_docker_cli' do
    cwd '/usr/local/src'
    user 'root'
    command 'yum install -y docker-ce-cli'
end

execute 'install_docker_containerd' do
    cwd '/usr/local/src'
    user 'root'
    command 'yum install -y containerd.io'
end

#
execute 'install_docker_compose' do
    cwd '/usr/local/src'
    user 'root'
    command 'yum install -y docker-compose'
end

# Allow vagrant user to run docker
execute 'add_vagrant_docker' do
    cwd '/usr/local/src'
    user 'root'
    command 'usermod -aG docker vagrant'
end

service 'docker' do
  action [ :enable, :start]
end

log 'Installed Blackrain Docker CE Engine'
