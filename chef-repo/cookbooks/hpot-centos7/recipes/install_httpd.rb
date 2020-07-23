
#cp /vagrant/apache/minimal-index.html /var/www/html/index.html
#chown apache:apache /var/www/html/index.html
#chmod 755 /var/www/html/index.html#
#cp /vagrant/apache/minimal-httpd.conf /etc/httpd/httpd.conf

package 'httpd'
package 'httpd-devel'
package 'mod_ssl'
package 'php'

cookbook_file "/etc/httpd/httpd.conf" do
   source "hpot-httpd.conf"
   mode "0644"
   owner 'apache'
   group 'apache'
end

cookbook_file "/var/www/html/index.html" do
   source "hpot-index.html"
   mode "0755"
   owner 'apache'
   group 'apache'
end

# Copy a load of stuff from ppot project - i.e. download a zip file and unbundle
