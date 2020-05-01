#!/bin/bash -eux
# configure-sshd.sh

# Turn off sshd DNS lookup, it slows down the login process
#sudo echo "UseDNS no" >> /etc/ssh/sshd_config

# Disablng GSSAPI authentication, it slows down the login process
#sudo echo "GSSAPIAuthentication no" >> /etc/ssh/sshd_config
