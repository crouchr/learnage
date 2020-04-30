#!/usr/bin/env bash
# Upload the Box file to Vagrant
BOX_DIR=$1
BOX_VERSION=$2
VAGRANT_CLOUD_TOKEN=$3

# Derived
BOX_NAME="${BOX_DIR}".box

vagrant cloud auth whoami ${VAGRANT_CLOUD_TOKEN}

#vagrant \
#cloud publish \
#-d "RCH CentOS7 Box" \
#--force \
#crouchr/${BOX_DIR} ${BOX_VERSION} virtualbox boxes/${BOX_NAME}
