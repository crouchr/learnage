# ARGUS
# =====
#package 'libpcap'
#package 'libpcap-devel'
#package 'daq'
#package 'daq-devel'

execute 'get_argus_source' do
    cwd '/usr/local/src'
    user 'root'
    command 'curl -o /usr/local/src/argus-3.0.8.2.tar.gz http://web.ermin/br2020-packages/argus-3.0.8.2.tar.gz'
end

execute 'get_argus_clients_source' do
    cwd '/usr/local/src'
    user 'root'
    command 'curl -o /usr/local/src/argus-clients-3.0.8.2.tar.gz http://web.ermin/br2020-packages/argus-clients-3.0.8.2.tar.gz'
end

# Argus server
execute 'gunzip_argus' do
    cwd '/usr/local/src'
    command 'gunzip argus-3.0.8.2.tar.gz'
    user 'root'
end

execute 'untar_argus' do
    cwd '/usr/local/src'
    command 'tar xvf argus-3.0.8.2.tar'
    user 'root'
end

execute 'install_argus' do
    cwd '/usr/local/src/argus-3.0.8.2'
    command './configure'
    user 'root'
end

execute 'make_argus' do
    cwd '/usr/local/src/argus-3.0.8.2'
    command 'make'
    user 'root'
end

execute 'install_argus' do
    cwd '/usr/local/src/argus-3.0.8.2'
    command 'make install'
    user 'root'
end

# Argus clients
execute 'gunzip_argus_clients' do
    cwd '/usr/local/src'
    command 'gunzip argus-clients-3.0.8.2.tar.gz'
    user 'root'
end

execute 'untar_argus_clients' do
    cwd '/usr/local/src'
    command 'tar xvf argus-clients-3.0.8.2.tar'
    user 'root'
end

execute 'install_argus_clients' do
    cwd '/usr/local/src/argus-clients-3.0.8.2'
    command './configure'
    user 'root'
end

execute 'make_argus_clients' do
    cwd '/usr/local/src/argus-clients-3.0.8.2'
    command 'make'
    user 'root'
end

execute 'install_argus' do
    cwd '/usr/local/src/argus-clients-3.0.8.2'
    command 'make install'
    user 'root'
end




log 'Installed Argus'