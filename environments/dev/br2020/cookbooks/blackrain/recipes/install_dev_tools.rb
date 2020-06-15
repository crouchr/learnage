# DEV TOOLS
# =========
# Need to reduce this to bare minimum once its all working - and to uninstall them at the end ?
# These are the packages needed to install applications natively in the VM
# Packages needed to build the DOcker images are handled in the Dockerfiles


# What was needing cmake ?
# What was needing git ?
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

# to be removed
# electric fence was for honeytrap
# libemu looks like it is honeytrap
# libnetfilter looks like honeytrap
