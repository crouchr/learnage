# Removed these networking steps from the default recipe as it causes test-kitchen fails
# Have another recipe to add them in that is used outside of test kitchen
# disable IPv6 https://unixmen.com/disable-ipv6-centos-7/
# Dionaea will try to bind for IPv6
execute 'disable_ipv6' do
    user 'root'
    command 'sysctl -w net.ipv6.conf.all.disable_ipv6=1 && sysctl -w net.ipv6.conf.default.disable_ipv6=1'
end

# Set default route as via Internet
execute 'del_default_route' do
    user 'root'
    command 'route del default'
end

execute 'add_default_route' do
    user 'root'
    command 'route add default gw 192.168.1.1'
end

execute 'show_route_table' do
    user 'root'
    command 'route -n'
end
