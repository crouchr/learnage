#!/usr/bin/env bash
# Zero Out empty space on disk to improve compression
set -e	# bomb out if any problem

echo "Clean up root partition..."
sudo dd if=/dev/zero of=/zero.fill bs=1M || echo "dd exit code $? is suppressed"
sudo rm -f /zero.fill;

# Zero Out empty space in /boot
echo "Clean up /boot partition..."
count=`df --sync -kP /boot | tail -n1 | awk -F ' ' '{print $4}'`;
sudo dd if=/dev/zero of=/boot/zero.fill bs=1024 count=$count || echo "dd exit code $? is suppressed"
sudo rm /boot/zero.fill;

# Zero Out empty space in swap - not needed in VBox
#echo "Clean up swap partitions"
#swappart=`cat /proc/swaps | tail -n1 | awk -F ' ' '{print $1}'`
#swapoff $swappart;
#dd if=/dev/zero of=$swappart bs=1M || echo "dd exit code $? is suppressed"
#mkswap $swappart > /dev/null 2>&1;
#swapon $swappart;

# Sync to ensure delete completes
sudo sync
sudo sync
