# ClamAV Sniffer
# ==============
# https://github.com/rfxn/linux-malware-detect
execute 'get_clamav_sniffer_source' do
    cwd '/usr/local/src'
    user 'root'
    command 'curl -o /usr/local/src/clamav-sniffer-0.17.tgz http://web.ermin/br2020-packages/clamav-sniffer-0.17.tgz'
end

execute 'unzip_clamav_sniffer' do
    cwd '/usr/local/src'
    command 'gunzip clamav-sniffer-0.17.tgz'
    user 'root'
end

execute 'tar_clamav_sniffer' do
    cwd '/usr/local/src'
    command 'tar xvf clamav-sniffer-0.17.tar'
    user 'root'
end

execute 'configure_clamav_sniffer' do
    cwd '/usr/local/src/clamav-sniffer-0.17'
    command './configure'
    user 'root'
end

execute 'make_clamav_sniffer' do
    cwd '/usr/local/src/clamav-sniffer-0.17'
    command 'make'
    user 'root'
end
execute 'install_clamav_sniffer' do
    cwd '/usr/local/src/clamav-sniffer-0.17'
    command 'make install'
    user 'root'
end

log 'Installed ClamAV Sniffer'
