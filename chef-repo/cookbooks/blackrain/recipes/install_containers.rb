# This could probably be optimised to use a loop
# registry is the hostname of the registry it is a VM

execute 'install_amun_container' do
  cwd '/usr/local/src'
  user 'root'
  command 'docker pull registry:5000/amun:1.0.0'
end

execute 'install_cowrie_container' do
  cwd '/usr/local/src'
  user 'root'
  command 'docker pull registry:5000/cowrie:1.0.0'
end

execute 'install_glastofp_container' do
  cwd '/usr/local/src'
  user 'root'
  command 'docker pull registry:5000/glastopf:1.0.0'
end

execute 'install_waf_container' do
  cwd '/usr/local/src'
  user 'root'
  command 'docker pull registry:5000/waf:1.0.0'
end

execute 'install_honeytrap_container' do
  cwd '/usr/local/src'
  user 'root'
  command 'docker pull registry:5000/honeytrap:1.0.0'
end

execute 'install_p0f2_container' do
  cwd '/usr/local/src'
  user 'root'
  command 'docker pull registry:5000/p0f2:1.0.0'
end

execute 'install_netflow_container' do
  cwd '/usr/local/src'
  user 'root'
  command 'docker pull registry:5000/netflow:1.0.0'
end

execute 'install_microlinux_container' do
  cwd '/usr/local/src'
  user 'root'
  command 'docker pull registry:5000/microlinux:1.0.0'
end

execute 'install_scantools_container' do
  cwd '/usr/local/src'
  user 'root'
  command 'docker pull registry:5000/scantools:1.0.0'
end

execute 'install_dionaea_container' do
  cwd '/usr/local/src'
  user 'root'
  command 'docker pull registry:5000/dionaea:1.0.0'
end

log 'Installed Blackrain containers'
