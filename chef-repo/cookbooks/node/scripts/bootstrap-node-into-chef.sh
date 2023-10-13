# Run this script to bootstrap the Test Kitchen node into my Chef Server
# use with chef-client 12+
knife bootstrap --sudo --connection-user vagrant --connection-password vagrant \
-N default-centos7box.vagrantup.com \
--ssh-verify-host-key default-centos7box.vagrantup.com
