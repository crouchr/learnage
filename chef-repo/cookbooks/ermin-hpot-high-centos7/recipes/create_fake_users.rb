# Add groups first so they can be referenced when users are added
# https://yurisk.info/2010/06/04/top-10-usernames-used-in-ssh-brute-force/
# These are just some juicy accounts for brute force attackers to use

group 'admin' do
  append                true
  comment               'Admin group'
  gid                   1500
end

group 'supervisor' do
  append                true
  comment               'Supervisor 1 group'
  gid                   1501
end

group 'nagios' do
  append                true
  comment               'Nagios group'
  gid                   1502
end

group 'test' do
  append                true
  comment               'Test users group'
  gid                   1503
end

group 'oracle' do
  append                true
  comment               'DB users group'
  gid                   1504
end

group 'rancid' do
  append                true
  comment               'Rancid users group'
  gid                   1505
end

user 'admin' do
  password 'admin'
  comment 'Administrator'
  uid 1500
  gid 'admin'
  home '/home/admin'
  manage_home true
  shell '/bin/bash'
end

user 'supervisor' do
  password 'supervisor'
  comment 'Administrator'
  uid 1501
  gid 'supervisor'
  home '/home/supervisor'
  manage_home true
  shell '/bin/bash'
end

user 'nagios' do
  password 'nagios'
  comment 'Nagios'
  uid 1502
  gid 'nagios'
  home '/home/nagios'
  manage_home true
  shell '/bin/bash'
end

user 'test' do
  password 'test'
  comment 'Test User'
  uid 1503
  gid 'test'
  home '/home/test'
  manage_home true
  shell '/bin/bash'
end

user 'oracle' do
  password 'oracle'
  comment 'Oracle Test User'
  uid 1504
  gid 'oracle'
  home '/home/oracle'
  manage_home true
  shell '/bin/bash'
end

user 'rancid' do
  password 'rancid'
  comment 'RANCID User'
  uid 1505
  gid 'rancid'
  home '/home/rancid'
  manage_home true
  shell '/bin/bash'
end

log 'Created fake users'