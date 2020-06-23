# Maldet
# ======
execute 'get_maldet_source' do
    cwd '/usr/local/src'
    user 'root'
    command 'curl -o /usr/local/src/linux-malware-detect-master.zip http://web.ermin/br2020-packages/linux-malware-detect-master.zip'
end

execute 'unzip_maldet' do
    cwd '/usr/local/src'
    command 'unzip linux-malware-detect-master.zip'
    user 'root'
end

# This will also trigger a download of the latest signatures
execute 'install_maldet' do
    cwd '/usr/local/src'
    command './install'
    user 'root'
end

log 'Installed Maldet'
