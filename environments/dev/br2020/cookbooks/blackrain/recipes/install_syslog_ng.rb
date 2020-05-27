# Install syslog-ng

# https://www.syslog-ng.com/community/b/blog/posts/installing-latest-syslog-ng-on-rhel-and-other-rpm-distributions

code_stub = 'syslog-ng-2.0.10'

package 'glib2-devel'

execute 'get_syslog_ng_source' do
    cwd '/usr/local/src'
    user 'root'
    command 'curl -o /usr/local/src/#{code_stub}.tar.gz http://web.ermin/br2020-packages/#{code_stub}.tar.gz'
end
execute 'get_eventlog_source' do
    cwd '/usr/local/src'
    user 'root'
    command 'curl -o /usr/local/src/eventlog_0.2.12.tar.gz http://web.ermin/br2020-packages/eventlog_0.2.12.tar.gz'
end

# EVENTLOG
# --------

execute 'gunzip_seventlog' do
    cwd '/usr/local/src'
    command 'gunzip eventlog_0.2.12.tar.gz'
    user 'root'
end

execute 'untar_syslog_ng' do
    cwd '/usr/local/src'
    command 'tar xvf eventlog_0.2.12.tar'
    user 'root'
end

execute 'install_syslog_ng' do
    cwd '/usr/local/src/eventlog_0.2.12'
    command './configure'
    user 'root'
end

execute 'make_syslog_ng' do
    cwd '/usr/local/src/eventlog_0.2.12'
    command 'make'
    user 'root'
end



# SYSLOG-NG
# ---------

execute 'gunzip_syslog_ng' do
    cwd '/usr/local/src'
    command 'gunzip #{code_stub}.tar.gz'
    user 'root'
end

execute 'untar_syslog_ng' do
    cwd '/usr/local/src'
    command 'tar xvf #{code_stub}.tar'
    user 'root'
end

execute 'install_syslog_ng' do
    cwd '/usr/local/src/#{code_stub}'
    command './configure'
    user 'root'
end

execute 'make_syslog_ng' do
    cwd '/usr/local/src/#{code_stub}'
    command 'make'
    user 'root'
end

cookbook_file "/etc/syslog-ng.conf" do
  source "syslog-ng.conf"
  mode "0644"
end

service 'syslog-ng' do
  action [ :enable, :start]
end

package 'rsyslog' do
  action [ :remove]
end
