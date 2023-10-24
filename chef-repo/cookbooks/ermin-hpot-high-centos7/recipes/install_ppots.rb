
# The dummy web-site used to make the honeypot look semi-legit
remote_file '/tmp/hpot-tmp/ppots.tar.gz' do
  source        'http://web.ermin.lan/br2020-packages/ppots.tar.gz'
  owner         'root'
  group         'root'
  mode          '0755'
  action        :create
end

archive_file 'unarchive_ppots_website' do
  destination      '/var/www'
  group            'apache'
  mode             '755'
  overwrite        true
  owner            'apache'
  path             '/tmp/hpot-tmp/ppots.tar.gz'
  action           :extract
end

log 'Installed ppots.com dummy web-site'