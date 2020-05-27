# Install syslog-ng
# TODO - caopy across the blackrain config file

# https://www.syslog-ng.com/community/b/blog/posts/installing-latest-syslog-ng-on-rhel-and-other-rpm-distributions

#yum install syslog-ng
#systemctl enable syslog-ng
#systemctl start syslog-ng
#yum erase rsyslog

package 'syslog-ng'

cookbook_file "/etc/syslog-ng.conf" do
  source "syslog-ng.conf"
  mode "0644"
end

service 'syslog-ng' do
  action [ :enable, :start]
end

service 'rsyslog' do
  action [ :stop, :remove]
end
