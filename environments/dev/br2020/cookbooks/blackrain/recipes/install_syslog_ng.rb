# Install syslog-ng

# https://www.syslog-ng.com/community/b/blog/posts/installing-latest-syslog-ng-on-rhel-and-other-rpm-distributions
# https://documentation.solarwinds.com/en/Success_Center/loggly/Content/admin/syslog-ng-manual-configuration.htm
# https://www.syslog-ng.com/technical-documents/doc/syslog-ng-open-source-edition/3.25/administration-guide/13
# additionla configure args : https://www.linuxquestions.org/questions/linux-newbie-8/pkg-config-path-672477/

# https://www.tutorialspoint.com/chef/chef_environment_variable.htm
ENV['PKG_CONFIG_PATH'] = '/usr/local/lib/pkgconfig'

package 'glib2-devel'

# EVENTLOG
# --------
execute 'get_eventlog_source' do
    cwd '/usr/local/src'
    user 'root'
    command 'curl -o /usr/local/src/eventlog_0.2.12.tar.gz http://web.ermin/br2020-packages/eventlog_0.2.12.tar.gz'
end

execute 'gunzip_eventlog' do
    cwd '/usr/local/src'
    command 'gunzip eventlog_0.2.12.tar.gz'
    user 'root'
end

execute 'untar_eventlog' do
    cwd '/usr/local/src'
    command 'tar xvf eventlog_0.2.12.tar'
    user 'root'
end

execute 'configure_eventlog' do
    cwd '/usr/local/src/eventlog-0.2.12'
    command './configure'
    user 'root'
end

execute 'make_eventlog' do
    cwd '/usr/local/src/eventlog-0.2.12'
    command 'make'
    user 'root'
end

execute 'install_eventlog' do
    cwd '/usr/local/src/eventlog-0.2.12'
    command 'make install'
    user 'root'
end

execute 'add_libevent' do
    cwd '/usr/local/src/eventlog-0.2.12'
    command 'echo "/usr/local/lib" > /etc/ld.so.conf.d/local.conf'
    user 'root'
end

# ldconfig -p : should indicate that libevent-2.0.so.5 is visible to ldconfig
execute 'add_libevent' do
    cwd '/usr/local/src/eventlog-0.2.12'
    command 'ldconfig'
    user 'root'
end

# SYSLOG-NG
# ---------
execute 'get_syslog_ng_source' do
    cwd '/usr/local/src'
    user 'root'
    command 'curl -o /usr/local/src/syslog-ng-2.0.10.tar.gz http://web.ermin/br2020-packages/syslog-ng-2.0.10.tar.gz'
end

execute 'gunzip_syslog_ng' do
    cwd '/usr/local/src'
    command 'gunzip syslog-ng-2.0.10.tar.gz'
    user 'root'
end

execute 'untar_syslog_ng' do
    cwd '/usr/local/src'
    command 'tar xvf syslog-ng-2.0.10.tar'
    user 'root'
end

execute 'install_syslog_ng' do
    cwd '/usr/local/src/syslog-ng-2.0.10'
    command './configure --enable-dynamic-linking'
    user 'root'
end

execute 'make_syslog_ng' do
    cwd '/usr/local/src/syslog-ng-2.0.10'
    command 'make'
    user 'root'
end

execute 'install_syslog_ng' do
    cwd '/usr/local/src/syslog-ng-2.0.10'
    command 'make install'
    user 'root'
end

cookbook_file "/etc/syslog-ng.conf" do
  source "syslog-ng.conf"
  mode "0644"
end

package 'rsyslog' do
  action [ :remove]
end

# Need to write the rc.local equiv script ?
#service 'syslog-ng' do
#  action [ :enable, :start]
#end