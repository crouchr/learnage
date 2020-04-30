#!/bin/bash
# Script to build WAF CentOS 7 image using Packer
# This file can be deleted once a Jenkins job has been made to work

# -eux : e=exit on failure

# Adding -debug here means each step is paused until human presses ENTER

BOX_VERSION="1.0.1"

# Set PACKER_LOG=1 for more detail
export PACKER_LOG=0

date

AWS_PROFILE="developmentaws"

BOX_DESCRIPTION="Packer-built WAF Box"
BOX_NAME="rch-waf.box"
PACKER_FILE="waf-vbox-centos7.json"

echo " "
echo "Validate the WAF Packer file"
echo "----------------------------"
packer validate -var-file=waf-variables.json ${PACKER_FILE}

echo
echo "Build the WAF Vagrant box"
echo "-------------------------"
packer build \
-force -timestamp-ui \
-var-file=waf-variables.json \
-var "vm_description=${BOX_DESCRIPTION}" \
-var "vm_version=${BOX_VERSION}" \
${PACKER_FILE}

echo
echo "Add the WAF Vagrant box"
echo "------------------------"
vagrant box add rch-waf boxes/${BOX_NAME} --force

echo
echo "Upload the WAF Vagrant to Vagrant Cloud"
echo "---------------------------------------"
vagrant cloud publish -d "${BOX_DESCRIPTION}" --force crouchr/rch-waf ${BOX_VERSION} virtualbox boxes/${BOX_NAME}

echo " "
echo "Upload the WAF Vagrant box to my NVM S3 bucket"
echo "----------------------------------------------"
echo "Note : This may take several minutes..."
aws s3 --profile=${AWS_PROFILE} \
cp boxes/${BOX_NAME} s3://richardcrouch/boxes/${BOX_NAME}

echo " "
echo "Finished OK"
