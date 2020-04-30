#!/bin/bash -e
# CI/CD script
# Script to build CentOS 7 image using Packer for applications that need more storage e.g. spacewalk, artifactory (32GB HDD)
# This file can be deleted once a Jenkins job has been made to work

# -eux : e=exit on failure

# Adding -debug here means each step is paused until human presses ENTER

BOX_VERSION="1.0.2"

# Set PACKER_LOG=1 for more detail
export PACKER_LOG=0

date

AWS_PROFILE="developmentaws"

BOX_DESCRIPTION="Packer-built CentOS7 box (32GB)"
BOX_NAME="rch-centos7-32gig.box"
BOX_DIR="rch-centos7-32gig"
PACKER_FILE="virtualbox-centos7.json"

#echo "Changing directory into the centos7 packer root directory..."
# Note : pwd gives : /home/crouchr/PycharmProjects/network-team/experiments/richard-centos7-packer/hellobox
#pwd

echo " "
echo "Validate the CentOS7 (32 GB) Packer file"
echo "----------------------------------------"
packer validate -var-file=variables-32gig.json ${PACKER_FILE}

#echo
#echo "Build the CentOS7 (32 GB) Vagrant box"
#echo "-------------------------------------"
#packer build \
#-force -timestamp-ui \
#-var-file=variables-32gig.json \
#-var "vm_description=${BOX_DESCRIPTION}" \
#-var "vm_version=${BOX_VERSION}" \
#${PACKER_FILE}

#echo
#echo "Add the CentOS7 (32 GB) Vagrant box"
#echo "-----------------------------------"
#vagrant box add rch-centos7-32gig boxes/${BOX_NAME} --force

#echo
#echo "Upload the CentOS7 (32 GB) Vagrant to Vagrant Cloud"
#echo "---------------------------------------------------"
#vagrant cloud publish \
#--force \
#--release \
#crouchr/rch-centos7-32gig \
#${BOX_VERSION} \
#virtualbox \
#boxes/${BOX_NAME}

#echo " "
#echo "Upload the CentOS7 (32 GB) Vagrant box to my NVM S3 bucket"
#echo "----------------------------------------------------------"
#echo "Note : This may take several minutes..."
#aws s3 --profile=${AWS_PROFILE} \
#cp boxes/${BOX_NAME} s3://richardcrouch/boxes/${BOX_NAME}

#echo " "
#echo "Upload the CentOS7 (32 GB) Vagrant box to local web.ermin web server"
#echo "--------------------------------------------------------------------"
#echo "Note : This may take several minutes..."
#ssh web.ermin "mkdir -p /var/www/html/boxes/${BOX_DIR}/${BOX_VERSION}/virtualbox"
#scp boxes/${BOX_NAME} web.ermin:/var/www/html/boxes/${BOX_DIR}/${BOX_VERSION}/virtualbox/

echo
echo "Generate & upload the CentOS7 (32 GB) Vagrant box meta file"
echo "-----------------------------------------------------------"
cd boxes/${BOX_DIR}
rm -f metadata.json
vagrant-metadata \
--name="web.ermin/${BOX_DIR}" \
--description="${BOX_DESCRIPTION}" \
--baseurl="http://web.ermin/boxes/${BOX_DIR}"

cat metadata.json
scp -i /home/crouchr/.ssh/rch-nvm-sshkey metadata.json crouchr@web.ermin:/var/www/html/boxes/${BOX_DIR}

echo " "
echo "Finished OK"
