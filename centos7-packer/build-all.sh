#!/bin/bash
# Script to build all my Packer images

echo " "
echo "build-all.sh started"
date
echo " "

pwd

#echo
#echo "Build CentOS 7 images"
#echo "#####################"
build-centos7.sh
build-centos7-32gig.sh
build-micro-centos7.sh

#echo
#echo "Build WAF image"
#echo "################"
#./build-waf.sh

#echo
#echo "Build BlackRain2020 image"
#echo "##########################"
#cd ../../blackrain
#./build-blackrain.sh

echo
date
echo "build-all.sh finished OK"

