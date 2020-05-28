execute 'pip_pytest' do
    cwd '/usr/local/src'
    command 'pip install pytest'
    user 'root'
end


