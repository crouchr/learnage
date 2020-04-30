#!/usr/bin/env bash
#AWS_PROFILE=$1      # e.g. developmentaws
#BOX_DIR=$2         # e.g. rch-centos7
#BOX_VERSION=$3      # e.g. 1.0.1
#BOX_NAME="$BOX_DIR".box
AWS_PROFILE="developmentaws"

echo
echo "Upload the Vagrant box to my NVM S3 bucket"
echo "------------------------------------------"
echo "Note : This may take several minutes..."
echo "AWS_PROFILE is ${AWS_PROFILE}"
#echo "BOX_DIR is ${BOX_DIR}"
#echo "BOX_VERSION is ${BOX_VERSION}"
#echo "BOX_NAME is ${BOX_NAME}"

aws s3 \
--profile=${AWS_PROFILE} \
cp boxes/dummy.box s3://richardcrouch/boxes/dummy.box

#cp boxes/${BOX_DIR}/${BOX_VERSION}/${BOX_NAME} s3://richardcrouch/boxes/${BOX_NAME}
