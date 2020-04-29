#!/bin/bash -e
# Script called manually to build BlackRain CentOS 7 image using Packer
# -eux : e=exit on failure

####################
BOX_VERSION="1.0.13"            # Manually increment this
####################

# Set PACKER_LOG=1 for more detail
export PACKER_LOG=0
date
whoami
AWS_PROFILE="developmentaws"
BOX_DESCRIPTION="Packer-built BlackRain2020 box"
BOX_DIR="blackrain2020"
BOX_NAME="${BOX_DIR}.box"
PACKER_FILE="blackrain2020-vbox.json"
VAR_FILE="blackrain2020-variables.json"

echo
echo "Validate the BlackRain2020 Packer file"
echo "--------------------------------------"
packer validate \
-var-file=${VAR_FILE} \
-var "vm_description=${BOX_DESCRIPTION}" \
-var "vm_version=${BOX_VERSION}" \
${PACKER_FILE}

echo
echo "Build the BlackRain2020 Vagrant box"
echo "-----------------------------------"
packer build \
-force \
-timestamp-ui \
-var-file=${VAR_FILE} \
-var "vm_name=$BOX_DIR" \
-var "vm_description=${BOX_DESCRIPTION}" \
-var "build_directory=boxes" \
-var "box_version=${BOX_VERSION}" \
${PACKER_FILE}

echo " "
echo "Upload the BlackRain2020 Vagrant box to local web.ermin web server"
echo "------------------------------------------------------------------"
echo "SCPing ${BOX_NAME} to web.ermin..."
ssh web.ermin "mkdir -p /var/www/html/boxes/${BOX_DIR}/${BOX_VERSION}/virtualbox"
scp boxes/${BOX_DIR}/${BOX_VERSION}/virtualbox/${BOX_NAME} web.ermin:/var/www/html/boxes/${BOX_DIR}/${BOX_VERSION}/virtualbox/

echo
echo "Generate & upload the BlackRain2020 Vagrant box meta file"
echo "---------------------------------------------------------"
cd boxes/${BOX_DIR}
rm -f metadata.json
echo "Generating box metadata..."
vagrant-metadata \
--append \
--name="web.ermin/${BOX_DIR}" \
--description="${BOX_DESCRIPTION}" \
--baseurl="http://web.ermin/boxes/${BOX_DIR}"

cat metadata.json
scp -i /home/crouchr/.ssh/rch-nvm-sshkey metadata.json crouchr@web.ermin:/var/www/html/boxes/${BOX_DIR}

##scp -i /home/jenkins/.ssh/jenkins-ermin-keys metadata.json jenkins@web.ermin:/var/www/html/boxes/${BOX_DIR}

echo
date
echo "Finished OK"
