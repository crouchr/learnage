## install mariadb
# https://mariadb.com/resources/blog/installing-mariadb-10-on-centos-7-rhel-7/
# see https://www.ossec.net/docs/manual/output/mysql-database-output.html
# https://www.ossec.net/docs/manual/output/database-output.html
sudo su -
# start the database
systemctl start mariadb
systemctl status mariadb

mysql_secure_installation

# root password is sec....ql
[root@mars-ossec mariadb]# mysql_secure_installation

#NOTE: RUNNING ALL PARTS OF THIS SCRIPT IS RECOMMENDED FOR ALL MariaDB
#      SERVERS IN PRODUCTION USE!  PLEASE READ EACH STEP CAREFULLY!
#
#In order to log into MariaDB to secure it, we'll need the current
#password for the root user.  If you've just installed MariaDB, and
#you haven't set the root password yet, the password will be blank,
#so you should just press enter here.
#
#Enter current password for root (enter for none):
#OK, successfully used password, moving on...
#
#Setting the root password ensures that nobody can log into the MariaDB
#root user without the proper authorisation.
#
#Set root password? [Y/n] y
#New password:
#Re-enter new password:
#Password updated successfully!
#Reloading privilege tables..
# ... Success!
#
#
#By default, a MariaDB installation has an anonymous user, allowing anyone
#to log into MariaDB without having to have a user account created for
#them.  This is intended only for testing, and to make the installation
#go a bit smoother.  You should remove them before moving into a
#production environment.
#
#Remove anonymous users? [Y/n] Y
# ... Success!
#
#Normally, root should only be allowed to connect from 'localhost'.  This
#ensures that someone cannot guess at the root password from the network.
#
#Disallow root login remotely? [Y/n] Y
# ... Success!
#
#By default, MariaDB comes with a database named 'test' that anyone can
#access.  This is also intended only for testing, and should be removed
#before moving into a production environment.
#
#Remove test database and access to it? [Y/n] Y
# - Dropping test database...
# ... Success!
# - Removing privileges on test database...
# ... Success!
#
#Reloading the privilege tables will ensure that all changes made so far
#will take effect immediately.
#
#Reload privilege tables now? [Y/n] Y
# ... Success!
#
#Cleaning up...
#
#All done!  If you've completed all of the above steps, your MariaDB
#installation should now be secure.
#
#Thanks for using MariaDB!
#[root@mars-ossec mariadb]#



# cut and paste the following
mysql -u root -p
create database ossec;
grant INSERT,SELECT,UPDATE,CREATE,DELETE,EXECUTE on ossec.* to ossecuser@localhost;
set password for ossecuser@localhost=PASSWORD('ossecpass1968');
flush privileges;
quit

# ossec is the name of the database
# use sec...sql when prompted for password
cd /tmp/ossec-hids-2.8.3/src/os_dbd
mysql -u root -p ossec < mysql.schema


# add following to /var/ossec/etc/ossec.conf
<ossec_config>
    <database_output>
        <hostname>localhost</hostname>
        <username>ossecuser</username>
        <password>ossecpass1968</password>
        <database>ossec</database>
        <type>mysql</type>
    </database_output>
</ossec_config>

# run the following
/var/ossec/bin/ossec-control enable database
/var/ossec/bin/ossec-control restart

# ossec-dbd should be running
ossecm   23135  0.2  0.1 129080  3492 ?        S    07:40   0:00 /var/ossec/bin/ossec-dbd
