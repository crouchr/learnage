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
