
# logging is already in vbox image
#execute 'add_logging_to_hosts' do
#    cwd '/usr/local/src/glastopf'
#    user 'root'
#    command 'echo 192.168.1.106 logging.ermin logging >> /etc/hosts'
#end

# This is failing
execute 'add_mongodb_to_hosts' do
    cwd '/usr/local/src/glastopf'
    user 'root'
    command "echo '192.168.1.107 mongodb.ermin mongodb' >> /etc/hosts"
end

log 'Installed hosts file'
