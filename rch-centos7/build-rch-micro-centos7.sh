#!/bin/bash -e
# CI/CD script
# Script to build micro CentOS 7 image using Packer (16GB HDD)
# This file can be deleted once a Jenkins job has been made to work

# -eux : e=exit on failure

# Adding -debug here means each step is paused until human presses ENTER

BOX_VERSION="1.0.8"

# Set PACKER_LOG=1 for more detail
export PACKER_LOG=0

date

AWS_PROFILE="developmentaws"

BOX_DESCRIPTION="Packer-built Micro CentOS7 box"
BOX_NAME="rch-micro-centos7.box"
BOX_DIR="rch-micro-centos7"
PACKER_FILE="micro-virtualbox-centos7.json"
PACKER_VARS_FILE="micro-centos7-variables.json"

echo "Changing directory into the centos7 packer root directory..."

echo " "

# Note : pwd gives : /home/crouchr/PycharmProjects/network-team/experiments/richard-centos7-packer/hellobox
pwd

echo " "
echo "Validate the Micro CentOS7 Packer file"
echo "--------------------------------------"
packer validate -var-file=${PACKER_VARS_FILE} ${PACKER_FILE}

#echo
#echo "Build the Micro CentOS7 Vagrant box"
#echo "-----------------------------------"
#packer build \
#-force -timestamp-ui \
#-var-file=${PACKER_VARS_FILE} \
#-var "vm_description=${BOX_DESCRIPTION}" \
#-var "vm_version=${BOX_VERSION}" \
#${PACKER_FILE}

#echo
#echo "Upload the Micro CentOS7 Vagrant to Vagrant Cloud"
#echo "-------------------------------------------------"
#vagrant cloud publish \
#--force \
#--release \
#crouchr/rch-micro-centos7 \
#${BOX_VERSION} \
#virtualbox \
#boxes/${BOX_NAME}

#echo " "
#echo "Upload the CentOS7 Vagrant box to my NVM S3 bucket"
#echo "--------------------------------------------------"
#echo "Note : This may take several minutes..."
#aws s3 --profile=${AWS_PROFILE} \
#cp boxes/${BOX_NAME} s3://richardcrouch/boxes/${BOX_NAME}

echo " "
echo "Upload the Micro CentOS7 (32 GB) Vagrant box to local web.ermin web server"
echo "--------------------------------------------------------------------------"
echo "Note : This may take several minutes..."
ssh web.ermin "mkdir -p /var/www/html/boxes/${BOX_DIR}/${BOX_VERSION}/virtualbox"
scp boxes/${BOX_NAME} web.ermin:/var/www/html/boxes/${BOX_DIR}/${BOX_VERSION}/virtualbox/

echo " "
echo "Finished OK"

