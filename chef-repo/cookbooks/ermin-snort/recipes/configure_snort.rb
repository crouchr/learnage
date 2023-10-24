#
# Cookbook:: configure-snort
# Recipe:: default
#
# Copyright:: 2023, The Authors, All Rights Reserved.

template '/etc/snort.conf' do
  source 'snort.conf.erb'
  mode '0644'
  variables(
    :rule_path => node['snort']['rule_path'],
    :home_net => node['snort']['home_net'],
    :alert_full => node['snort']['alert_full'],
    :smtp_preproc_ports => node['snort']['smtp_preproc']['ports']
  )
end
