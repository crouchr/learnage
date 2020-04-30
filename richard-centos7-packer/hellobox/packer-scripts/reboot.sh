#!/bin/bash -eux

# Reboot: Required after updates to ensure VBox Guest Additions install correctly
# Sleep:  Required after reboot to ensure next packer script doesn't start before reboot

echo "reboot.sh : Reboot will take 60 seconds, please wait..."
sudo reboot
sleep 60

#sleep 3600