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




# package 'policycoreutils-python'
# package 'container-selinux'
#
# execute 'get_docker-selinux_package' do
#     cwd '/tmp'
#     user 'root'
#     command 'curl -k -o /tmp/docker-ce-selinux-17.03.3.ce-1.el7.noarch.rpm https://web.ermin/br2020-packages/docker-ce-selinux-17.03.3.ce-1.el7.noarch.rpm'
# end
# #
# execute 'get_containerd_package' do
#     cwd '/tmp'
#     user 'root'
#     command 'curl -k -o /tmp/containerd.io-1.2.13-3.2.el7.x86_64.rpm http://web.ermin/br2020-packages/containerd.io-1.2.13-3.2.el7.x86_64.rpm'
# end
# #
# execute 'get_docker_package' do
#     cwd '/tmp'
#     user 'root'
#     command 'curl -k -o /tmp/docker-ce-19.03.10-3.el7.x86_64.rpm http://web.ermin/br2020-packages/docker-ce-19.03.10-3.el7.x86_64.rpm'
# end
# #
# execute 'get_docker_cli_package' do
#     cwd '/tmp'
#     user 'root'
#     command 'curl -k -o /tmp/docker-ce-cli-19.03.10-3.el7.x86_64.rpm http://web.ermin/br2020-packages/docker-ce-cli-19.03.10-3.el7.x86_64.rpm'
# end
# #
# rpm_package 'docker-ce-selinux' do
#     action :install
#     source '/tmp/docker-ce-selinux-17.03.3.ce-1.el7.noarch.rpm'
# end
# #
# rpm_package 'containerd' do
#     action :install
#     source '/tmp/containerd.io-1.2.13-3.2.el7.x86_64.rpm'
# end
# #
# rpm_package 'docker-ce' do
#     action :install
#     source '/tmp/docker-ce-19.03.10-3.el7.x86_64.rpm'
# end
# #
# rpm_package 'docker-ce-cli' do
#     action :install
#     source '/tmp/docker-ce-cli-19.03.10-3.el7.x86_64.rpm'
# end
# #
# service 'containerd' do
#   action [ :enable, :start]
# end
# #
# service 'docker' do
#   action [ :enable, :start]
# end


