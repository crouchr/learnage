#!/bin/bash -eux
# Install telgraf on node - Chef will be used to configure it
# Put influxdb on another node
# https://www.digitalocean.com/community/tutorials/how-to-monitor-system-metrics-with-the-tick-stack-on-centos-7
set -e	# bomb out if any problem

sudo wget --no-check-certificate \
   http://web.ermin/br2020-packages/influxdata.repo \
   -O /etc/yum.repos.d/influxdata.repo

sudo yum -y install telegraf
