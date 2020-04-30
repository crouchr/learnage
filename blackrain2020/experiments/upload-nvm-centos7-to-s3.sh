#!/bin/bash -e
# Author : Richard Crouch
# Script called manually to upload nvm test kitchen CentOS into my NVM S3 bucket

BOX_NAME="centos-7.7.virtualbox.box"
AWS_PROFILE="developmentaws"

echo
echo "Upload the NVM CentOS7 Vagrant box to my NVM S3 bucket"
echo "------------------------------------------------------"
date
echo "Note : This may take several minutes..."

aws s3 --profile=${AWS_PROFILE} \
cp /home/crouchr/${BOX_NAME} s3://richardcrouch

echo
date
echo "Finished OK"
