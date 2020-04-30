# This has never been tested

AWS_PROFILE="developmentaws"
BOX_NAME="rch-centos-7.box"

echo "Upload the Vagrant box to my NVM S3 bucket"
echo "------------------------------------------"
echo "Note : This may take several minutes..."
aws s3 --profile=${AWS_PROFILE} \
cp boxes/${BOX_NAME} s3://richardcrouch
