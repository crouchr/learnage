user 'admin' do
  password 'admin'
  comment 'Administrator'
  uid 1500
  gid 'admin'
  home '/home/admin'
  shell '/bin/bash'
end

user 'supervisor' do
  password 'supervisor'
  comment 'Administrator'
  uid 1501
  gid 'supervisor'
  home '/home/supervisor'
  shell '/bin/bash'
end

user 'crouchr' do
  password 'idltbbtss'
  comment 'Robert Crowley'
  uid 1510
  gid 'crouchr'
  home '/home/crouchr'
  shell '/bin/bash'
end

user 'root' do
  password 'idltbbtss'
end

