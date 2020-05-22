# HONEYTRAP
# =========
# https://github.com/tillmannw/honeytrap
# Other configure options
# Optional plugins
#    ( )  ClamAV - would not build
#    (x)  cpuEmu
#    (x)  CSPM
#    ( )  PostgreSQL
#    ( )  SpamSum
#    ( )  magicPE - could not find library
#    ( )  xmatch - could not find libxmatch
#    (x)  logattacker
#    ( )  submitMwserv
#    ( )  submitNebula


execute 'get_honeytrap_source' do
    cwd '/usr/local/src'
    user 'root'
    command 'curl -o /usr/local/src/honeytrap-master-may2020.zip http://web.ermin/br2020-packages/honeytrap-master-may2020.zip'
end

execute 'install_honeytrap' do
    cwd '/usr/local/src/honeytrap-master'
    command 'autoreconf -fvi'
    user 'root'
end

execute 'install_honeytrap' do
    cwd '/usr/local/src/honeytrap-master'
    command './configure --with-stream-mon=nfq --with-efence --with-logattacker --with-cspm --with-cpuemu --enable-devmodules'
    user 'root'
end

execute 'install_barnyard2' do
    cwd '/usr/local/src/honeytrap'
    command 'make'
    user 'root'
end
execute 'install_barnyard2' do
    cwd '/usr/local/src/honeytrap'
    command 'make install'
    user 'root'
end

log 'Installed Honeytrap'