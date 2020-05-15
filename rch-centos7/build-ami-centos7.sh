#!/bin/bash -e
# README : Used for building according to the AMI ks file

# CI/CD script
# -eux : e=exit on failure

# Set by Jenkins
BOX_VERSION="0.0.1"
BOX_DESCRIPTION="Box based on AMI Kick Starter"

# Set PACKER_LOG=1 for more detail
export PACKER_LOG=1

date

#AWS_PROFILE="developmentaws"
BOX_DIR="ami-centos7"
BOX_NAME="${BOX_DIR}.box"
PACKER_FILE="${BOX_DIR}-packer.json"
VAR_FILE="${BOX_DIR}-variables.json"

echo "BOX_DIR     : ${BOX_DIR}"
echo "BOX_NAME    : ${BOX_NAME}"
echo "PACKER_FILE : ${PACKER_FILE}"
echo "VAR_FILE    : ${VAR_FILE}"

echo
pwd
echo " "
echo "Validate the CentOS7 Packer file"
echo "--------------------------------"
/usr/local/bin/packer validate \
-var-file=${VAR_FILE} \
-var "vm_description=${BOX_DESCRIPTION}" \
-var "vm_version=${BOX_VERSION}" \
${PACKER_FILE}

# Build with headless=false for debugging purposes
echo
echo "Build the CentOS7 Vagrant box"
echo "-----------------------------"
/usr/local/bin/packer build \
-force \
-timestamp-ui \
-var-file=${VAR_FILE} \
-var "vm_name=$BOX_DIR" \
-var "vm_description=${BOX_DESCRIPTION}" \
-var "build_directory=boxes" \
-var "box_version=${BOX_VERSION}" \
-var 'headless=false' \
${PACKER_FILE}


echo " "
echo "Finished OK"
