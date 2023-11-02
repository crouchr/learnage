# install wui
# first install ossec and configure database

# as root
cd /tmp
unzip ossec-wui-0.8.zip
mv ossec-wui-master /var/www/ossec-wui
mv /var/www/ossec-wui/ /var/www/html/
cd /var/www/html/ossec-wui
./setup.sh

# add these by hand
# usermod -G ossec apache
# chmod 770 /tmp
# chgrp apache /tmp

# Fix PHP by hand /etc/php.ini
#[Date]
#; Defines the default timezone used by the date functions
#; http://www.php.net/manual/en/datetime.configuration.php#ini.date.timezone
#date.timezone = 'Europe/London'

# reboot the node

# point browser at
# http://192.168.1.85/ossec-wui/index.php