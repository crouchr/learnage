package 'mod_security'
package 'mod_security_crs'
package 'mod_security-mlogc'

cookbook_file '/etc/httpd/conf.d/mod_security.conf' do
   source 'mod_security.conf'
   mode  '0644'
   owner 'apache'
   group 'apache'
end

# restart HTTPd
service 'httpd' do
  action :restart
end

# enable HTTPd
service 'httpd' do
  action :enable
end
