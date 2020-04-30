#!/bin/bash -eux
#
# Setup Custom Init script
#
# Configure the VM to run a script on startup
#

# Create the custom_init script file
cat <<EOF > /etc/init.d/custom_init
#!/bin/bash

FLAG="/var/log/firstboot.log"
if [ ! -f \$FLAG ]; then
   # Initialise the VM as required
   logger First Boot. Starting VM Init..

   mkdir -p /media/cdrom
   mount -o loop /dev/cdrom /media/cdrom

   /media/cdrom/vm_init.sh

   umount /media/cdrom

   logger "VM Init Complete!"

   # Create the flag file to prevent running again on reboot
   touch \$FLAG
else
   echo "Do nothing"
fi
EOF

# Make the script executable
chmod +x /etc/init.d/custom_init

# Add to rc.local
cat <<EOF >> /etc/rc.local

/etc/init.d/custom_init
EOF
