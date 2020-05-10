#!/usr/bin/env bash
# see https://www.redhat.com/archives/spacewalk-list/2017-June/msg00016.html
sudo systemctl disable rhnsd
sudo systemctl disable rhnmd
sudo sed -i 's/enabled *= *1/enabled=0/' /etc/yum/pluginconf.d/rhnplugin.conf
