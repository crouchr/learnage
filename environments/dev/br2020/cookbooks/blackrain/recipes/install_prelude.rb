# PRELUDE
# =======
execute 'get_libprelude_source' do
    cwd '/usr/local/src'
    user 'root'
    command 'curl -o /usr/local/src/libprelude-5.1.1.tar.gz http://web.ermin/br2020-packages/libprelude-5.1.1.tar.gz'
end

execute 'unzip_libprelude_source' do
    cwd '/usr/local/src'
    user 'root'
    command 'gunzip libprelude-5.1.1.tar.gz'
end

execute 'untar_libprelude_source' do
    cwd '/usr/local/src'
    user 'root'
    command 'tar xvf libprelude-5.1.1.tar'
end

execute 'make_configure' do
    cwd '/usr/local/src/libprelude-5.1.1'
    user 'root'
    command './configure'
end

execute 'make_libprelude' do
    cwd '/usr/local/src/libprelude-5.1.1'
    user 'root'
    command 'make'
end

execute 'install_libprelude' do
    cwd '/usr/local/src/libprelude-5.1.1'
    user 'root'
    command 'make install'
end

package 'prelude-manager-db-plugin'
package 'prelude-lml'
package 'prelude-lml-rules'
package 'prelude-correlator'
## fails : package 'python3-prewikka'
package 'prelude-tools'
package 'preludedb-tools'
package 'preludedb-mysql'
