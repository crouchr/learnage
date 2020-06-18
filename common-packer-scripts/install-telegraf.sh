#!/bin/bash -eux

# Put influxdb on another node

# https://www.digitalocean.com/community/tutorials/how-to-monitor-system-metrics-with-the-tick-stack-on-centos-7

sudo wget --no-check-certificate \
   http://web.ermin/br2020-packages/influxdata.repo \
   -O /etc/yum.repos.d/influxdata.repo

# I don't have a file yet
#sudo wget --no-check-certificate \
#   http://web.ermin/br2020-packages/telegraf.conf \
#   -O /etc/telegraf/telegraf.conf

sudo yum -y install telegraf

