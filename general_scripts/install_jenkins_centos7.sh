#!/usr/bin/env bash
# Source : https://linuxize.com/post/how-to-install-jenkins-on-centos-7/
# Just cut and paste the commands - this is not tested to run as a script yet
sudo yum install java-1.8.0-openjdk-devel
curl --silent --location http://pkg.jenkins-ci.org/redhat-stable/jenkins.repo | sudo tee /etc/yum.repos.d/jenkins.repo
sudo rpm --import https://jenkins-ci.org/redhat/jenkins-ci.org.key
sudo yum install jenkins
sudo systemctl start jenkins
systemctl status jenkins
sudo systemctl enable jenkins

#sudo firewall-cmd --permanent --zone=public --add-port=8080/tcp
#sudo firewall-cmd --reload

# test by pointing browser to http://your_ip_or_domain:8080
#sudo cat /var/lib/jenkins/secrets/initialAdminPassword

# install the following plugins
# green balls
# github authentication
# build time blame plugin
# cobertura
# disk-usage
# build monitor view
# sonarqube scanning for jenkins
# ssh plugin
# violations plugin
# virtualbox plugin
# workspace cleanup
# powershell

