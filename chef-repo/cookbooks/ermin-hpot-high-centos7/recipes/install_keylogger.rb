# Install the key logger

#directory '/tmp/.commands' do
#  owner 'root'
#  group 'root'
#  mode '0777'
#  action :create
#end

# FIXME : Set full permissions until have tested
# ideally the users cannot read it
file '/tmp/.commands.log' do
  owner 'root'
  group 'root'
  mode  '0777'
end

# FIXME : can I tighten permissions to hide this from other users ?
cookbook_file "/home/admin/.bashrc" do
   source "dot-bashrc-for-logging.txt"
   mode "0644"
end

log 'Installed keylogger'