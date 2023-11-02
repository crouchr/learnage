# Install ossec-server
# you must be root to run this
cd /tmp
cp GeoLiteCity.dat /var/ossec/etc/
tar xvf ossec-hids-2.8.3.tar.gz
cd ossec-hids-2.8.3
cd src
make setgeoip
make setdb
cd ..

# now run the ossec installer
DATABASE=mysql ./install.sh
./install.sh

# make setdb

# add the following to ossec.conf
# -------------------------------
#  <global>
#    <email_notification>no</email_notification>
#    <logall>yes</logall>
#   </global>
#
#  <syslog_output>
#     <server>192.168.1.55</server>
#     <port>5514</port>
#     <level>6</level>
#  </syslog_output>

# run /var/ossec/bin/ossec-control enable client-syslog
## run /var/ossec/bin/ossec-control enable database
# run /var/ossec/bin/ossec-control restart


MariaDB [ossec]> show databases;
MariaDB [ossec]> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| ossec              |
| performance_schema |
+--------------------+
4 rows in set (0.00 sec)

MariaDB [ossec]> use ossec;
Database changed
MariaDB [ossec]> show tables;
+----------------------------+
| Tables_in_ossec            |
+----------------------------+
| agent                      |
| alert                      |
| category                   |
| data                       |
| location                   |
| server                     |
| signature                  |
| signature_category_mapping |
+----------------------------+
8 rows in set (0.00 sec)

