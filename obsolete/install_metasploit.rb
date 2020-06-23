# Install Metasploit
# also do Owasp ZAP

#curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall && \
#  chmod 755 msfinstall && \
#  ./msfinstall

# On pause

execute 'get_metasploit_source' do
    cwd '/usr/local/src'
    user 'root'
    command 'curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall'
end

execute 'chmod_msfinstall' do
    cwd '/usr/local/src'
    command 'chmod 755 msfinstall'
    user 'root'
end

execute 'install_metasploit' do
    cwd '/usr/local/src'
    command './msfinstall'
    user 'root'
end

