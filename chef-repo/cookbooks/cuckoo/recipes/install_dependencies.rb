#
# Cookbook:: cuckoo
# Recipe::
#
# Copyright:: 2020, The Authors, All Rights Reserved.

package 'libffi-dev'
package 'libssl-dev'
package 'libjpeg-dev'
package 'zlib1g-dev'

# Django WebUI
package 'mongodb'

package 'postgresql'
package 'libpq-dev'

# tcpdump - must not run as root
package 'tcpdump'
package 'apparmor-utils'
package 'libcap2-bin'
execute 'aa_disable_tcpdump' do
  command 'aa-disable /usr/sbin/tcpdump'
  user 'root'
end
execute 'group_add_pcap' do
  command 'groupadd pcap'
  user 'root'
end

execute 'usermod_pcap' do
  command 'usermod -a -G pcap cuckoo'
  user 'root'
end

execute 'chgrp_pcap' do
  command 'chgrp pcap /usr/sbin/tcpdump'
  user 'root'
end

execute 'setcap_pcap' do
  command 'setcap cap_net_raw,cap_net_admin=eip /usr/sbin/tcpdump'
  user 'root'
end

