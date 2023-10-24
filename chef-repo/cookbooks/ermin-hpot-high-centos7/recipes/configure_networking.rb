# Removed these networking steps from the default recipe as it causes test-kitchen fails
# This recipe assumes IPv6 has been disabled in the base box file

# Set default route as via Internet
execute 'del_default_route' do
    user 'root'
    command 'route del default'
end

execute 'add_default_route' do
    user 'root'
    command 'route add default gw 192.168.1.1'
end

log 'Configured networking'
