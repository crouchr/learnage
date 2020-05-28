# GeoIP
# =====
package 'python-devel'
package 'GeoIP-devel'

execute 'get_geoip_database' do
    cwd '/usr/local/share'
    user 'root'
    command 'curl -o /usr/local/share/GeoLiteCity.dat.gz http://web.ermin/br2020-packages/GeoLiteCity.dat.gz'
end

execute 'gunzip_geoip_database' do
    cwd '/usr/local/share'
    command 'gunzip GeoLiteCity.dat.gz'
    user 'root'
end

execute 'pip_geoip' do
    cwd '/usr/local/src'
    command 'pip install GeoIP'
    user 'root'
end

log 'Installed GeoIP City Lite Database'
