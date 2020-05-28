#!/usr/bin/env bash
# reference : https://computingforgeeks.com/how-to-install-jfrog-artifactory-on-centos/

# START HERE
whoami

# java
# ----
sudo yum -y install java-1.8.0-openjdk java-1.8.0-openjdk-devel
#sudo alternatives --config java
java -version

sudo echo "# The line(s) below added by setup.sh" >> /etc/hosts
sudo echo "192.168.1.100 spacewalk.ermin spackewalk" >> /etc/hosts
sudo echo "192.168.1.101 artifactory.ermin artifactory" >> /etc/hosts

sudo echo "# The line below added by setup.sh" >> /home/vagrant/.bashrc
sudo echo "export JAVA_HOME=$(dirname $(dirname $(readlink $(readlink $(which javac)))))" >> /home/vagrant/.bashrc
source ~/.bashrc
export PATH=$PATH:$JAVA_HOME/bin
export CLASSPATH=.:$JAVA_HOME/jre/lib:$JAVA_HOME/lib:$JAVA_HOME/lib/tools.jar
echo $JAVA_HOME
echo $PATH
echo $CLASSPATH

# Get Artifactory repos and setup environemnt for later
curl -sL https://bintray.com/jfrog/artifactory-rpms/rpm | sudo tee /etc/yum.repos.d/bintray-jfrog-artifactory-rpms.repo
sudo echo "export ARTIFACTORY_HOME=/opt/jfrog/artifactory" | sudo tee -a /etc/profile
source /etc/profile
env | grep ARTIFACTORY_HOME

# MariaDB - it is not installed by default
# ----------------------------------------
#sudo yum remove mariadb-server
cat <<EOF | sudo tee /etc/yum.repos.d/MariaDB.repo
[mariadb]
name = MariaDB
baseurl = http://yum.mariadb.org/10.4/centos7-amd64
gpgkey=https://yum.mariadb.org/RPM-GPG-KEY-MariaDB
gpgcheck=1
EOF

# Clean yum cache index
sudo yum makecache fast

sudo yum -y install MariaDB-server MariaDB-client
rpm -qi MariaDB-server
sudo systemctl enable --now mariadb

echo "Now 'vagrant ssh' into the node and continue with the steps shown at https://computingforgeeks.com/install-mariadb-10-on-ubuntu-18-04-and-centos-7/"

echo "Artifactory installation complete"
