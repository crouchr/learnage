#!/usr/bin/env bash
# see https://www.redhat.com/archives/spacewalk-list/2017-June/msg00016.html
set -e	# bomb out if any problem

echo "De-register from Spacewalk"
echo "EARLY EXIT : IGNORE THIS DUE TO BUG"
exit
sudo systemctl disable rhnsd
sudo sed -i 's/enabled *= *1/enabled=0/' /etc/yum/pluginconf.d/rhnplugin.conf
