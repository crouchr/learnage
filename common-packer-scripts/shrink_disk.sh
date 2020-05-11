#!/usr/bin/env bash
# Zero Out empty space on disk to improve compression
echo "Clean disk(s)..."

dd if=/dev/zero of=/zero.fill bs=1M || echo "dd exit code $? is suppressed"
rm -f /zero.fill;

# Zero Out empty space in /boot
echo "Clean up /boot"
count=`df --sync -kP /boot | tail -n1 | awk -F ' ' '{print $4}'`;
dd if=/dev/zero of=/boot/zero.fill bs=1024 count=$count || echo "dd exit code $? is suppressed"
rm /boot/zero.fill;

# Zero Out empty space in swap - not needed in VBox
#echo "Clean up swap partitions"
#swappart=`cat /proc/swaps | tail -n1 | awk -F ' ' '{print $1}'`
#swapoff $swappart;
#dd if=/dev/zero of=$swappart bs=1M || echo "dd exit code $? is suppressed"
#mkswap $swappart > /dev/null 2>&1;
#swapon $swappart;

# Sync to ensure delete completes
sync
sync
