# DEV TOOLS
# =========
# Need to reduce this to bare minimum once its all working - and to uninstall them at the end ?
package 'gcc'
package 'gcc-c++'
package 'autoconf'
package 'automake'
package 'bison'
package 'byacc'
package 'flex'
package 'cmake'
package 'git'
package 'libtool'
package 'unzip'
package 'python-devel'
package 'GeoIP-devel'
package 'yum-utils'

# https://github.com/grpc/grpc/issues/17812
#package 'centos-release-scl'
#execute 'install_gcc7' do
#    cwd '/usr/local/src'
#    user 'root'
#    command 'yum install -y devtoolset-7-gcc*'
#end

#execute 'install_gcc7' do
#    cwd '/usr/local/src'
#    user 'root'
#    command 'scl enable devtoolset-7 bash'
#end

# LIBRARIES
# =========
package 'gnutls'
package 'gnutls-devel'
package 'libdnet'
package 'libdnet-devel'
package 'libnet-devel'
package 'libnetfilter_queue-devel'
package 'ElectricFence'
package 'libemu-devel'
package 'libpcap-devel'
