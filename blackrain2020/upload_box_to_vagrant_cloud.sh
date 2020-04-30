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

# Login
vagrant cloud auth login ${VAGRANT_CLOUD_TOKEN}

# Display some basic information
vagrant cloud auth whoami ${VAGRANT_CLOUD_TOKEN}

# Push the file to Vagrant Cloud
vagrant \
cloud publish \
--description "${BOX_DESCRIPTION}" \
--short-description "${BOX_DESCRIPTION}" \
--force \
--release \
--box-version ${BOX_VERSION} \
crouchr/${BOX_DIR} ${BOX_VERSION} virtualbox boxes/${BOX_DIR}/${BOX_VERSION}/virtualbox/${BOX_NAME}
