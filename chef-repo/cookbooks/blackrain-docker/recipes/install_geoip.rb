# GeoIP
# =====
package 'python-devel'
package 'GeoIP-devel'

# get rid of this if it works
# execute 'get_geoip_database' do
#    cwd '/usr/local/share'
#    user 'root'
#    command 'curl -o /usr/local/share/GeoIP/GeoLiteCity.dat.gz http://web.ermin/br2020-packages/GeoLiteCity.dat.gz'
# end

remote_file '/usr/local/share/GeoIP/GeoLiteCity.dat.gz' do
  source 'http://web.ermin/br2020-packages/GeoLiteCity.dat.gz'
  owner 'vagrant'
  group 'vagrant'
  mode '0755'
  action :create
end

execute 'gunzip_geoip_database' do
  cwd '/usr/local/share/GeoIP'
  command 'gunzip GeoLiteCity.dat.gz'
  user 'root'
end

execute 'pip_geoip' do
  cwd '/usr/local/src'
  command 'pip install GeoIP'
  user 'root'
end

log 'Installed GeoIP City (Lite) Database'
