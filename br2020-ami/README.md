ref : https://computingforgeeks.com/build-aws-ec2-machine-imges-with-packer-and-ansible/

cd ~/projects/packer-ansible-aws/packer
packer build -machine-readable packer-build.json | tee build_artifact.txt
