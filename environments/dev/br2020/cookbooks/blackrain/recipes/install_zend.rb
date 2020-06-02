# Install Bro IDS
# There is also a 2.X version

# https://easy-admin.ca/index.php/2017/03/21/install-bro-on-centos-7-x6-x/

#sudo yum install cmake make gcc gcc-c++ flex bison libpcap-devel openssl-devel python-devel swig zlib-devel perl

package 'openssl-devel'
package 'swig'
package 'zlib-devel'
package 'ncurses-devel'

execute 'get_zeek_source' do
    cwd '/usr/local/src'
    user 'root'
    command 'curl -o /usr/local/src/zeek-3.0.6.tar.gz http://web.ermin/br2020-packages/zeek-3.0.6.tar.gz'
end

execute 'gunzip_zeek' do
    cwd '/usr/local/src'
    command 'gunzip zeek-3.0.6.tar.gz'
    user 'root'
end

execute 'untar_zeek' do
    cwd '/usr/local/src'
    command 'tar xvf zeek-3.0.6.tar'
    user 'root'
end

execute 'configure_zeek' do
    cwd '/usr/local/src/zeek-3.0.6'
    command './configure'
    user 'root'
end

execute 'make_zeek' do
    cwd '/usr/local/src/zeek-3.0.6'
    command 'make'
    user 'root'
end

execute 'install_zeek' do
    cwd '/usr/local/src/zeek-3.0.6'
    command 'make install'
    user 'root'
end
