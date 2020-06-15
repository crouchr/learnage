# This could probably be optimised to use a loop

execute 'install_amun_container' do
    cwd '/usr/local/src'
    user 'root'
    command 'docker install -t cicd/amun:v1.0.0'
end

execute 'install_cowrie_container' do
    cwd '/usr/local/src'
    user 'root'
    command 'docker install -t cicd/cowrie:v1.0.0'
end

execute 'install_glastofp_container' do
    cwd '/usr/local/src'
    user 'root'
    command 'docker install -t cicd/glastopf:v1.0.0'
end

execute 'install_honeytrap_container' do
    cwd '/usr/local/src'
    user 'root'
    command 'docker install -t cicd/honeytrap:v1.0.0'
end

execute 'install_p0f2_container' do
    cwd '/usr/local/src'
    user 'root'
    command 'docker install -t cicd/p0f2:v1.0.0'
end
