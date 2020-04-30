#!/bin/bash
# Script to build generic CentOS 7 image using Packer

# -eux : e=exit on failure

# Adding -debug here means each step is paused until human presses ENTER
# Set PACKER_LOG=1 for more detail
export PACKER_LOG=0
AWS_PROFILE="developmentaws"

PACKER_FILE="virtualbox-centos7.json"
BOX_NAME="rch-centos-7.box"

echo "Changing directory into the centos7 packer root directory..."
cd ../..

echo " "

# Note : pwd gives : /home/crouchr/PycharmProjects/network-team/experiments/richard-centos7-packer/hellobox
pwd

echo "Validate the Packer file"
echo "------------------------"
packer validate -var-file=variables.json ${PACKER_FILE}

echo
echo "Build the Vagrant box"
echo "---------------------"
packer build -force -timestamp-ui -var-file=variables.json ${PACKER_FILE}

#echo "Add the Vagrant box to local Vagrant"
#echo "------------------------------------"
# The name of the box is rch-sandboxCentOS-7
#vagrant box add rch-sandboxCentOS-7 boxes/sandbox_centos7.box --force

echo "Upload the Vagrant box to my NVM S3 bucket"
echo "------------------------------------------"
echo "Note : This may take several minutes..."
aws s3 --profile=${PROFILE} \
cp boxes/${BOX_NAME} s3://richardcrouch

echo " "
echo "Finished OK"
