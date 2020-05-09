#!/bin/bash -e
# CI/CD script
# -eux : e=exit on failure

# Set by Jenkins
BOX_VERSION=$1
BOX_DESCRIPTION=$2

# Set PACKER_LOG=1 for more detail
export PACKER_LOG=0

date

AWS_PROFILE="developmentaws"
BOX_DIR="blackrain2020"
BOX_NAME="${BOX_DIR}.box"
PACKER_FILE="${BOX_DIR}-packer.json"
VAR_FILE="${BOX_DIR}-variables.json"

echo
pwd
echo " "
echo "Validate the BlackRain Packer file"
echo "----------------------------------"
/usr/local/bin/packer validate \
-var-file=${VAR_FILE} \
-var "vm_description=${BOX_DESCRIPTION}" \
-var "vm_version=${BOX_VERSION}" \
${PACKER_FILE}

exit

#packer inspect ${PACKER_FILE}

# Jenkins needs headless=true
echo
echo "Build the BlackRain2020 Vagrant box"
echo "-----------------------------------"
/usr/local/bin/packer build \
-force \
-timestamp-ui \
-var-file=${VAR_FILE} \
-var "vm_name=$BOX_DIR" \
-var "vm_description=${BOX_DESCRIPTION}" \
-var "build_directory=boxes" \
-var "box_version=${BOX_VERSION}" \
-var 'headless=true' \
${PACKER_FILE}

#echo " "
#echo "Upload the BlackRain2020 Vagrant box to local web.ermin web server"
#echo "------------------------------------------------------------------"
#echo "SCPing ${BOX_NAME} to web.ermin..."
#ssh web.ermin "mkdir -p /var/www/html/boxes/${BOX_DIR}/${BOX_VERSION}/virtualbox"
#scp boxes/${BOX_DIR}/${BOX_VERSION}/virtualbox/${BOX_NAME} web.ermin:/var/www/html/boxes/${BOX_DIR}/${BOX_VERSION}/virtualbox/

#echo
#echo "Generate & upload the BlackRain2020 Vagrant box meta file"
#echo "---------------------------------------------------------"
#cd boxes/${BOX_DIR}
#rm -f metadata.json
#echo "Generating box metadata..."
#vagrant-metadata \
#--append \
#--name="web.ermin/${BOX_DIR}" \
#--description="${BOX_DESCRIPTION}" \
#--baseurl="http://web.ermin/boxes/${BOX_DIR}"

#
#cat metadata.json
#scp -i /home/crouchr/.ssh/rch-nvm-sshkey metadata.json crouchr@web.ermin:/var/www/html/boxes/${BOX_DIR}

##scp -i /home/jenkins/.ssh/jenkins-ermin-keys metadata.json jenkins@web.ermin:/var/www/html/boxes/${BOX_DIR}

#echo
#date
#echo "Finished OK"
