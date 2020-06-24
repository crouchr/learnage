package 'python-pip'

execute 'upgrade_pip' do
    cwd '/usr/local/src'
    command 'pip install --upgrade pip'
    user 'root'
end

# this wil be part of the blackrain code recipes
#execute 'pip_pytest' do
#    cwd '/usr/local/src'
#    command 'pip install pytest'
#    user 'root'
#end

# this wil be part of the blackrain code recipes
#execute 'pip_pytest' do
#    cwd '/usr/local/src'
#    command 'pip install tweepy'
#    user 'root'
#end
