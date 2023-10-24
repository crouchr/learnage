# SNORT
# =====
# Next version of this to build from latest 2.9 sources including daq

package 'libdnet' do
  action :install
end

package 'libdnet-devel' do
  action :install
end

remote_file '/tmp/snort-2.9.16-1.centos7.x86_64.rpm' do
  source 'http://web.ermin.lan/br2020-packages/snort-2.9.16-1.centos7.x86_64.rpm'
  owner 'vagrant'
  group 'vagrant'
  mode '0644'
  action :create
end

package 'install_snort' do
  action :install
  source '/tmp/snort-2.9.16-1.centos7.x86_64.rpm'
end

# https://unix.stackexchange.com/questions/209813/libdnet-is-installed-but-cant-be-found-by-snort
# ln -s /usr/lib64/libdnet.so.1.0.1 /usr/lib64/libdnet.1
link '/usr/lib64/libdnet.1' do
  to '/usr/lib64/libdnet.so.1.0.1'
  link_type :symbolic
end

log 'Installed Snort NIDS'
