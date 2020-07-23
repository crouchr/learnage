# Users that will login legitimately into the honeypot
group 'crouchr' do
  append                true
  comment               'Supervisor 2 group'
  gid                   1590
end

user 'crouchr' do
  password 'idltbbtss'
  comment 'Robert Crowley'
  uid 1590
  gid 'crouchr'
  home '/home/crouchr'
  manage_home true
  shell '/bin/bash'
end

group "add crouchr wheel" do
  group_name 'wheel'
  members 'crouchr'
  action :modify
  append true
end


