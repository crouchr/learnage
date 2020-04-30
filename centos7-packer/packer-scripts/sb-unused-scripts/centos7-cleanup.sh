#!/bin/bash -eux
#
# Template Cleanup script
#
# Cleanup disk and prep
#

# Store current disk usage
DISK_USAGE_BEFORE_CLEANUP=$(df -h)

# Clear out machine id
rm -f /etc/machine-id
touch /etc/machine-id

# Stop system logging
service rsyslog stop
service auditd stop

# Cleanup old package files
yum install -y yum-utils
package-cleanup -y --oldkernels --count=1
yum clean all

# Force log rotate and remove old log files
logrotate -f /etc/logrotate.conf
rm -rf /var/log/*-???????? /var/log/*.gz
rm -rf /var/log/dmesg.old
rm -rf /var/log/anaconda.*

# Truncate the logs we want to keep in place
cat /dev/null > /var/log/audit/audit.log
cat /dev/null > /var/log/wtmp
cat /dev/null > /var/log/lastlog
cat /dev/null > /var/log/grubby

# Clean out temp and cache files
rm -rf /tmp/* /var/tmp/*
rm -rf /var/cache/* /usr/share/doc/*

# Remove SSH host keys
rm -f /etc/ssh/*key*

# Remove root user history,keys, files etc
rm -f ~root/.bash_history
unset HISTFILE
rm -rf ~root/.ssh/
rm -f ~root/anaconda-ks.cfg

# Remove Core Files
rm -f /core*

# Rebuild RPM db
rpmdb --rebuilddb
rm -f /var/lib/rpm/__db*

# [portability: required for vm template]
# Remove MAC and UUID from ifcfg
sed -Ei '/^(HWADDR|UUID)=/d' /etc/sysconfig/network-scripts/ifcfg-e*
# Remove persistent device rules
rm -f /etc/udev/rules.d/70*

# Zero Out empty space on disk to improve compression
echo "Clean disks"
dd if=/dev/zero of=/zero.fill bs=1M || echo "dd exit code $? is suppressed"
rm -f /zero.fill;

# Zero Out empty space in /boot
echo "Clean up /boot"
count=`df --sync -kP /boot | tail -n1 | awk -F ' ' '{print $4}'`;
dd if=/dev/zero of=/boot/zero.fill bs=1024 count=$count || echo "dd exit code $? is suppressed"
rm /boot/zero.fill;

# Zero Out empty space in swap
echo "Clean up swap partitions"
swappart=`cat /proc/swaps | tail -n1 | awk -F ' ' '{print $1}'`
swapoff $swappart;
dd if=/dev/zero of=$swappart bs=1M || echo "dd exit code $? is suppressed"
mkswap $swappart > /dev/null 2>&1;
swapon $swappart;

# Sync to ensure delete completes
sync
sync

# Report status
echo "==> Disk usage before cleanup"
echo ${DISK_USAGE_BEFORE_CLEANUP}

echo "==> Disk usage after cleanup"
df -h

exit 0
