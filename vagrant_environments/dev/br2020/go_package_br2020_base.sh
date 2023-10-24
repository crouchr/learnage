#!/usr/bin/env bash
# This needs to be the last part of the Jenkins job - i.e. not done in an environment - but good for now
# docker, snort, clamav etc. i.e. not my code now will be installed on top of this box
# This box is then used for applying Blackrain application software onto - i.e. my code
# FIXME : Put the box in another place - not in current directory
echo "Package the Packer-built br2020 image into the baseline box (for infrastructure to be added into)"
BOX_VERSION=0.1.0
vagrant package --output br2020-base-v${BOX_VERSION}.box
