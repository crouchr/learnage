#!/usr/bin/env bash
# Upload the Box file to Vagrant
BOX_DIR=$1
BOX_VERSION=$2
BOX_DESCRIPTION=$3
VAGRANT_CLOUD_TOKEN=$4

# Derived
BOX_NAME="${BOX_DIR}".box

echo "BOX_DIR : ${BOX_DIR}"
echo "BOX_VERSION : ${BOX_VERSION}"
echo "BOX_DESCRIPTION : ${BOX_DESCRIPTION}"

vagrant cloud auth login ${VAGRANT_CLOUD_TOKEN}

vagrant cloud auth whoami ${VAGRANT_CLOUD_TOKEN}

vagrant \
cloud publish \
-d "${BOX_DESCRIPTION}" \
--force \
crouchr/${BOX_DIR} ${BOX_VERSION} virtualbox boxes/${BOX_DIR}/${BOX_VERSION}/virtualbox/${BOX_NAME}
