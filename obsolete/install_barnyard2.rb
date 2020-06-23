# BARNYARD
# ========
package 'libpcap'
package 'libpcap-devel'
package 'daq'
package 'daq-devel'

execute 'clone_barnyard2' do
   cwd '/usr/local/src'
   command 'git clone git://github.com/firnsy/barnyard2.git'
   user 'root'
end

# ref : http://howtododifficult.blogspot.com/2017/07/install-barnyard2-in-centos.html
execute 'install_barnyard2' do
    cwd '/usr/local/src/barnyard2'
    command 'autoreconf -fvi -I ./m4'
    user 'root'
end
execute 'install_barnyard2' do
    cwd '/usr/local/src/barnyard2'
    command './configure --enable-prelude'
    user 'root'
end
execute 'install_barnyard2' do
    cwd '/usr/local/src/barnyard2'
    command 'make'
    user 'root'
end
execute 'install_barnyard2' do
    cwd '/usr/local/src/barnyard2'
    command 'make install'
    user 'root'
end
log 'Installed Barnyard2'