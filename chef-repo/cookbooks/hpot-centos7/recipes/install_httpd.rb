# install Apache and PHP
#cp /vagrant/apache/minimal-index.html /var/www/html/index.html
#chown apache:apache /var/www/html/index.html
#chmod 755 /var/www/html/index.html#
#cp /vagrant/apache/minimal-httpd.conf /etc/httpd/httpd.conf

package 'httpd'
package 'httpd-devel'
package 'mod_ssl'
package 'php'
package 'php-mysql'

# need to add mod_sec

cookbook_file '/etc/httpd/httpd.conf' do
   source 'hpot-httpd.conf'
   mode  '0644'
   owner 'apache'
   group 'apache'
end

cookbook_file '/var/www/html/index.html' do
   source 'hpot-index.html'
   mode  '0755'
   owner 'apache'
   group 'apache'
end

# Add basic test file for PHP (& haxxors)
cookbook_file '/var/www/html/info.php' do
   source 'info.php'
   mode  '0755'
   owner 'apache'
   group 'apache'
end

# The dummy web-site used to make the honeypot look semi-legit
remote_file '/tmp/hpot-tmp/ppots.tar.gz' do
  source        'http://web.ermin.lan/br2020-packages/ppots.tar.gz'
  owner         'root'
  group         'root'
  mode          '0755'
  action        :create
end

archive_file 'unarchive_ppots_website' do
  destination      '/var/www'
  group            'apache'
  mode             '755'
  overwrite        true
  owner            'apache'
  path             '/tmp/hpot-tmp/ppots.tar.gz'
  action           :extract
end
