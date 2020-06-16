# This could probably be optimised to use a loop
# registry is the hostname of the registry it is a VM

execute 'install_amun_container' do
    cwd '/usr/local/src'
    user 'root'
    command 'docker pull registry/amun:1.0.0'
end

execute 'install_cowrie_container' do
    cwd '/usr/local/src'
    user 'root'
    command 'docker pull registry/cowrie:1.0.0'
end

execute 'install_glastofp_container' do
    cwd '/usr/local/src'
    user 'root'
    command 'docker pull registry/glastopf:1.0.0'
end

execute 'install_honeytrap_container' do
    cwd '/usr/local/src'
    user 'root'
    command 'docker pull registry/honeytrap:1.0.0'
end

execute 'install_p0f2_container' do
    cwd '/usr/local/src'
    user 'root'
    command 'docker pull registry/p0f2:1.0.0'
end

execute 'install_netflow_container' do
    cwd '/usr/local/src'
    user 'root'
    command 'docker pull registry/netflow:1.0.0'
end

execute 'install_microlinux_container' do
    cwd '/usr/local/src'
    user 'root'
    command 'docker pull registry/microlinux:1.0.0'
end
