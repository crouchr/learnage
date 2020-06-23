# Install Bro IDS
# There is also a 2.X version -> see if Zend is workable

# Failed at final make - DO NOT USE

# X509.cc: In static member function ‘static int X509_Cert::verifyChain(Contents_SSL*, const u_char*, uint32)’:
# X509.cc:195:47: error: cannot convert ‘_STACK* {aka stack_st*}’ to ‘stack_st_X509*’ in initialization
#  STACK_OF(X509)* untrustedCerts = sk_new_null();                                               ^
# X509.cc:236:41: error: cannot convert ‘stack_st_X509*’ to ‘_STACK* {aka stack_st*}’ for argument ‘1’ to ‘int sk_push(_STACK*, void*)’
#    sk_push(untrustedCerts, (char*) pTemp);
#                                         ^
# X509.cc:262:34: error: cannot convert ‘stack_st_X509*’ to ‘_STACK* {aka stack_st*}’ for argument ‘1’ to ‘void sk_pop_free(_STACK*, void (*)(void*))’
#  sk_pop_free(untrustedCerts, free);
#                                  ^
# make[3]: *** [X509.o] Error 1


# https://easy-admin.ca/index.php/2017/03/21/install-bro-on-centos-7-x6-x/

#sudo yum install cmake make gcc gcc-c++ flex bison libpcap-devel openssl-devel python-devel swig zlib-devel perl

package 'openssl-devel'
package 'swig'
package 'zlib-devel'
package 'ncurses-devel'

execute 'get_bro_source' do
    cwd '/usr/local/src'
    user 'root'
    command 'curl -o /usr/local/src/bro-1.5-release.tar.gz http://web.ermin/br2020-packages/bro-1.5-release.tar.gz'
end

execute 'gunzip_bro' do
    cwd '/usr/local/src'
    command 'gunzip bro-1.5-release.tar.gz'
    user 'root'
end

execute 'untar_bro' do
    cwd '/usr/local/src'
    command 'tar xvf bro-1.5-release.tar'
    user 'root'
end

execute 'configure_bro' do
    cwd '/usr/local/src/bro-1.5.1'
    command './configure'
    user 'root'
end

execute 'make_bro' do
    cwd '/usr/local/src/bro-1.5.1'
    command 'make'
    user 'root'
end

execute 'install_bro' do
    cwd '/usr/local/src/bro-1.5.1'
    command 'make install'
    user 'root'
end
