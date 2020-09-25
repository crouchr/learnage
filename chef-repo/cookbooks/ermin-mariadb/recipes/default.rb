#
# Cookbook:: ermin-mariadb
# Recipe:: default
#
# Copyright:: 2020, The Authors, All Rights Reserved.

# install
# yum install -y python-pip3 python3 python3-devel
# yum install -y mariadb-server
# pip3 install mysql-connector-python
# pip3 install mariadb
# Needed for mariadb-connector-c

execute 'install_okay' do
    user 'root'
    command 'yum install -y http://repo.okay.com.mx/centos/7/x86_64/release/okay-release-1-1.noarch.rpm'
end

package 'mariadb-server'
package 'mariadb-libs'
package 'mariadb-devel'
package 'mariadb-connector-c'

execute 'install_mysql_connector' do
    user 'root'
    command 'pip3 install mysql-connector-python'
end

execute 'install_mariadb' do
    user 'root'
    command 'pip3 install mariadb'
end
