# Glastopf
# ========
# unzip glastopf-master.zip
# https://www.cyberciti.biz/faq/how-to-install-php-7-2-on-centos-7-rhel-7/
# https://github.com/grpc/grpc/issues/17812

#cd /opt
#git clone git://github.com/mushorg/BFR.git
#cd BFR
#phpize
#./configure --enable-bfr
#make &&  make install

# NOT NEEDED - Use the Dockerised version

execute 'install_remi_repo' do
    cwd '/usr/local/src'
    user 'root'
    command 'yum install -y http://rpms.remirepo.net/enterprise/remi-release-7.rpm'
end

execute 'enable_remi_repo' do
    cwd '/usr/local/src'
    user 'root'
    command 'yum-config-manager --enable remi-php72'
end

package 'php72'
package 'php-devel'

execute 'clone_phpsandbox_source' do
    cwd '/usr/local/src'
    user 'root'
    command 'git clone git://github.com/mushorg/BFR.git'
end

execute 'phpize_phpsandbox' do
    cwd '/usr/local/src/BFR'
    user 'root'
    command 'phpize'
end

execute 'configure_phpsandbox' do
    cwd '/usr/local/src/BFR'
    user 'root'
    command './configure --enable-bfr'
end

# fails here - need gcc 6 or 7 ?
execute 'make_phpsandbox' do
    cwd '/usr/local/src/BFR'
    user 'root'
    command 'make'
end

execute 'install_phpsandbox' do
    cwd '/usr/local/src/BFR'
    user 'root'
    command 'make install'
end

# execute 'clone_glastopf_source' do
#     cwd '/usr/local/src'
#     user 'root'
#     command 'git clone https://github.com/mushorg/glastopf.git'
# end
#
# execute 'unzip_glastopf' do
#     cwd '/usr/local/src'
#     command 'unzip glastopf-master.zip'
#     user 'root'
# end
#
# execute 'tar_glastopf_sniffer' do
#     cwd '/usr/local/src'
#     command 'tar xvf clamav-sniffer-0.17.tar'
#     user 'root'
# end


