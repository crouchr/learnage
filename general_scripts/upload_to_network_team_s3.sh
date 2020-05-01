#!/usr/bin/env bash

FILE='/home/crouchr/CentOS7_v2_virtualbox.box'

AWS_PROFILE=developmentaws
S3_KEY=boxes

echo
echo "Upload a file to my NVM S3 bucket"
echo "---------------------------------"
echo "Note : This may take several minutes..."
echo "AWS_PROFILE is ${AWS_PROFILE}"
echo "File to be uploaded : ${FILE}"
echo "Uploading to S3..."

aws s3 \
--profile=${AWS_PROFILE} \
cp ${FILE} s3://richardcrouch/${S3_KEY}/
