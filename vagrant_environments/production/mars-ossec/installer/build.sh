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

MariaDB [ossec]> SELECT rule_id, level, description FROM signature;
+---------+-------+---------------------------------------------------------------------------------------------------+
| rule_id | level | description                                                                                       |
+---------+-------+---------------------------------------------------------------------------------------------------+
|       1 |     0 | Generic template for all syslog rules.                                                            |
|       2 |     0 | Generic template for all firewall rules.                                                          |
|       3 |     0 | Generic template for all ids rules.                                                               |
|       4 |     0 | Generic template for all web rules.                                                               |
|       5 |     0 | Generic template for all web proxy rules.                                                         |
|       6 |     0 | Generic template for all windows rules.                                                           |
|       7 |     0 | Generic template for all ossec rules.                                                             |
|    5500 |     0 | Grouping of the pam_unix rules.                                                                   |
|    5501 |     3 | Login session opened.                                                                             |
|    5502 |     3 | Login session closed.                                                                             |
|    5503 |     5 | User login failed.                                                                                |
|    5504 |     5 | Attempt to login with an invalid user.                                                            |
|    5521 |     0 | Ignoring Annoying Ubuntu/debian cron login events.                                                |
|    5522 |     0 | Ignoring Annoying Ubuntu/debian cron login events.                                                |
|    5523 |     0 | Ignoring events with a user or a password.                                                        |
|    5551 |    10 | Multiple failed logins in a small period of time.                                                 |
|    5552 |     0 | PAM and gdm are not playing nicely.                                                               |
|    5553 |     4 | PAM misconfiguration.                                                                             |
|    5554 |     4 | PAM misconfiguration.                                                                             |
|    5555 |     3 | User changed password.                                                                            |
|    5700 |     0 | SSHD messages grouped.                                                                            |
|    5701 |     8 | Possible attack on the ssh server (or version gathering).                                         |
|    5702 |     5 | Reverse lookup error (bad ISP or attack).                                                         |
|    5703 |    10 | Possible breakin attempt (high number of reverse lookup errors).                                  |
|    5704 |     4 | Timeout while logging in (sshd).                                                                  |
|    5705 |    10 | Possible scan or breakin attempt (high number of login timeouts).                                 |
|    5706 |     6 | SSH insecure connection attempt (scan).                                                           |
|    5707 |    14 | OpenSSH challenge-response exploit.                                                               |
|    5709 |     0 | Useless SSHD message without an user/ip and context.                                              |
|    5710 |     5 | Attempt to login using a non-existent user                                                        |
|    5711 |     0 | Useless/Duplicated SSHD message without a user/ip.                                                |
|    5712 |    10 | SSHD brute force trying to get access to the system.                                              |
|    5713 |     6 | Corrupted bytes on SSHD.                                                                          |
|    5714 |    14 | SSH CRC-32 Compensation attack                                                                    |
|    5715 |     3 | SSHD authentication success.                                                                      |
|    5716 |     5 | SSHD authentication failed.                                                                       |
|    5717 |     4 | SSHD configuration error (moduli).                                                                |
|    5718 |     5 | Attempt to login using a denied user.                                                             |
|    5719 |    10 | Multiple access attempts using a denied user.                                                     |
|    5720 |    10 | Multiple SSHD authentication failures.                                                            |
|    5721 |     0 | System disconnected from sshd.                                                                    |
|    5722 |     0 | ssh connection closed.                                                                            |
|    5723 |     0 | SSHD key error.                                                                                   |
|    5724 |     0 | SSHD key error.                                                                                   |
|    5725 |     0 | Host ungracefully disconnected.                                                                   |
|    5726 |     5 | Unknown PAM module, PAM misconfiguration.                                                         |
|    5727 |     0 | Attempt to start sshd when something already bound to the port.                                   |
|    5728 |     4 | Authentication services were not able to retrieve user credentials.                               |
|    5729 |     0 | Debug message.                                                                                    |
|    5730 |     4 | SSHD is not accepting connections.                                                                |
|    5731 |     6 | SSH Scanning.                                                                                     |

MariaDB [ossec]> SELECT * FROM alert;
+----+-----------+---------+------------+-------------+--------+--------+----------+----------+-----------------+
| id | server_id | rule_id | timestamp  | location_id | src_ip | dst_ip | src_port | dst_port | alertid         |
+----+-----------+---------+------------+-------------+--------+--------+----------+----------+-----------------+
|  1 |         1 |     531 | 1698910859 |           1 |      0 |      0 |        0 |        0 | 1698910859.4228 |
|  2 |         1 |     502 | 1698910864 |           2 |      0 |      0 |        0 |        0 | 1698910862.4504 |
+----+-----------+---------+------------+-------------+--------+--------+----------+----------+-----------------+
2 rows in set (0.00 sec)

MariaDB [ossec]> SELECT rule_id,location.name location, INET_NTOA(src_ip) srcip, full_log FROM alert,location, data WHERE location.id = alert.location_id AND data.id = alert.id AND data.server_id = alert.server_id;
+---------+----------------------------+---------+----------------------------------------------------------------------------------------------------------+
| rule_id | location                   | srcip   | full_log                                                                                                 |
+---------+----------------------------+---------+----------------------------------------------------------------------------------------------------------+
|     531 | mars-ossec->df -h          | 0.0.0.0 | ossec: output: `df -h`: /dev/loop0                41M   41M     0 100% /var/lib/snapd/snap/termshark/803 |
|     502 | mars-ossec->ossec-monitord | 0.0.0.0 | ossec: Ossec started.                                                                                    |
+---------+----------------------------+---------+----------------------------------------------------------------------------------------------------------+
2 rows in set (0.00 sec)
