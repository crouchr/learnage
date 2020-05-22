# FPROBE
# ======



execute 'get_fprobe_source' do
    cwd '/usr/local/src'
    user 'root'
    command 'curl -o /usr/local/src/fprobe_1.1.orig.tar.gz http://web.ermin/br2020-packages/fprobe_1.1.orig.tar.gz'
end

execute 'gunzip_fprobe' do
    cwd '/usr/local/src'
    command 'gunzip fprobe_1.1.orig.tar.gz'
    user 'root'
end

execute 'untar_fprobe' do
    cwd '/usr/local/src'
    command 'tar xvf fprobe_1.1.orig.tar'
    user 'root'
end

execute 'configure_fprobe' do
    cwd '/usr/local/src/fprobe_1.1'
    command './configure'
    user 'root'
end

execute 'make_fprobe' do
    cwd '/usr/local/src/probe-1.1'
    command 'make'
    user 'root'
end
execute 'install_fprobe' do
    cwd '/usr/local/src/probe-1.1'
    command 'make install'
    user 'root'
end

log 'Installed fprobe'