# This could probably be optimised to use a loop

execute 'install_amun_container' do
    cwd '/usr/local/src'
    user 'root'
    command 'docker pull cicd/amun:v1.0.0'
end

execute 'install_cowrie_container' do
    cwd '/usr/local/src'
    user 'root'
    command 'docker pull cicd/cowrie:v1.0.0'
end

execute 'install_glastofp_container' do
    cwd '/usr/local/src'
    user 'root'
    command 'docker pull cicd/glastopf:v1.0.0'
end

execute 'install_honeytrap_container' do
    cwd '/usr/local/src'
    user 'root'
    command 'docker pull cicd/honeytrap:v1.0.0'
end

execute 'install_p0f2_container' do
    cwd '/usr/local/src'
    user 'root'
    command 'docker pull cicd/p0f2:v1.0.0'
end

execute 'install_netflow_container' do
    cwd '/usr/local/src'
    user 'root'
    command 'docker pull cicd/netflow:v1.0.0'
end

execute 'install_microlinux_container' do
    cwd '/usr/local/src'
    user 'root'
    command 'docker pull cicd/microlinux:v1.0.0'
end
