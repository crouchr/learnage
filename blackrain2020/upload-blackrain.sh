#!/bin/bash -e
# Script called manually to build BlackRain CentOS 7 image using Packer
# -eux : e=exit on failure

BOX_VERSION="1.0.11"

# Set PACKER_LOG=1 for more detail
export PACKER_LOG=0

date

AWS_PROFILE="developmentaws"

BOX_DESCRIPTION="Packer-built BlackRain2020 box"
BOX_NAME="blackrain2020.box"
BOX_DIR="blackrain2020"

#echo
#echo "Add the BlackRain2020 Vagrant box locally"
#echo "-----------------------------------------"
#vagrant box add blackrain2020 boxes/${BOX_NAME} --force

#echo
#echo "Upload the BlackRain2020 Vagrant box to Vagrant Cloud"
#echo "-----------------------------------------------------"
#vagrant cloud publish \
#--force \
#--release \
#crouchr/blackrain2020 \
#${BOX_VERSION} \
#virtualbox \
#boxes/${BOX_NAME}

#echo
#echo "Upload the BlackRain2020 Vagrant box to my NVM S3 bucket"
#echo "--------------------------------------------------------"
#echo "Note : This may take several minutes..."
#aws s3 --profile=${AWS_PROFILE} \
#cp boxes/${BOX_NAME} s3://richardcrouch/boxes/${BOX_NAME}

#echo " "
#echo "Upload the BlackRain2020 Vagrant box to local web.ermin web server"
#echo "------------------------------------------------------------------"
#echo "Note : This may take several minutes..."
#ssh web.ermin "mkdir -p /var/www/html/boxes/${BOX_DIR}/${BOX_VERSION}/virtualbox"
#scp boxes/${BOX_NAME} web.ermin:/var/www/html/boxes/${BOX_DIR}/${BOX_VERSION}/virtualbox/

echo
echo "Generate & upload the BlackRain2020 Vagrant box meta file"
echo "---------------------------------------------------------"
cd boxes/${BOX_DIR}
rm -f metadata.json
vagrant-metadata \
--name="web.ermin/${BOX_DIR}" \
--description="${BOX_DESCRIPTION}" \
--baseurl="http://web.ermin/boxes/${BOX_DIR}"

cat metadata.json
scp -i /home/crouchr/.ssh/rch-nvm-sshkey metadata.json crouchr@web.ermin:/var/www/html/boxes/${BOX_DIR}

echo
date
echo "Finished OK"
