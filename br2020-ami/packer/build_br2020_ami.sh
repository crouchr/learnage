packer build \
-machine-readable \
-var aws_access_key=$AWS_ACCESS_KEY_ID \
-var aws_secret_key=$AWS_SECRET_ACCESS_KEY \
packer-build.json | tee build_artifact.txt

