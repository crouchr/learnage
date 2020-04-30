#!/usr/bin/env bash
# ref : https://pypi.org/project/vagrant-metadata/

BOX_NAME=nvm-centos7
METADATA_FILENAME=${BOX_NAME}-metadata.json

#vagrant-metadata \
#--name="crouchr/${BOX_NAME}" \
#--description="CentOS 7 NVM Test Kitchen 64-bit image" \
#--baseurl="http://web.ermin/boxes"

##vagrant-metadata \
##--append \
##--name="crouchr/rch-micro-centos7" \
##--description="CentOS 7 64-bit micro image" \
#--baseurl="http://web.ermin/boxes"
#

#mv metadata.json ${METADATA_FILENAME}

ls

scp -i /home/crouchr/.ssh/rch-nvm-sshkey ${METADATA_FILENAME} crouchr@web.ermin:/var/www/html/boxes/${METADATA_FILENAME}

