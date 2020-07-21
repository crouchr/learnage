
remote_file '/tmp/hpot-tmp/wazuh-agent-3.9.5-1.x86_64.rpm' do
  source 'http://web.ermin/br2020-packages/wazuh-agent-3.9.5-1.x86_64.rpm'
  owner 'root'
  group 'root'
  mode '0755'
  action :create
end

rpm_package 'wazuh-agent' do
  source               '/tmp/hpot-tmp/wazuh-agent-3.9.5-1.x86_64.rpm'
end
