# SNORT
# =====
execute 'install_snort' do
  command 'yum -y install http://web.ermin/br2020-packages/snort-2.9.16-1.centos7.x86_64.rpm'
  user 'root'
end

log 'Installed Snort NIDS'
