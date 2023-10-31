# Install ossec-server
# you must be root to run this
cd /tmp
cp GeoLiteCity.dat /var/ossec/etc/
tar xvf ossec-hids-2.8.3.tar.gz
cd ossec-hids-2.8.3
cd src
make setgeoip
cd ..

# now run the ossec installer
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
