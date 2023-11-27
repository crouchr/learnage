#!/usr/bin/env bash
# Bring up the SonarQube - intent is bring up a pet based on this script
# This script assumes a CentOS host
# Files on the Host can be accessed via the /vagrant share

set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning VCC SonarQube node"

# Check for patch updates - slows up boot so need a way of avoiding this
yum update -y --disableplugin=fastestmirror

yum install -y wget curl unzip

tee -a /etc/sysctl.conf<<EOF
# Added during Vagrant run
vm.max_map_count=262144
fs.file-max=65536
# End of added during Vagrant run
EOF

#echo "[+] Premature exit to facilitate troubleshooting"
#exit 0

sysctl --system

echo "[+] Add sonar user"
#adduser sonar
#echo "[+] Set sonar user password"
#echo sonar:myson65-ssword | chpasswd
useradd --system --no-create-home sonar

# install Java
wget -q -O /tmp/jdk-17_linux-x64_bin.rpm https://download.oracle.com/java/17/latest/jdk-17_linux-x64_bin.rpm
yum -y install /tmp/jdk-17_linux-x64_bin.rpm
# Java smoke check
java -version

# Configure node
cp /vagrant/config/motd /etc/

# FIXME - move to start of file
SONAR_VERSION='10.3.0.82913'
echo "[+] Download SonarQube v${SONAR_VERSION}"
wget -q -O /tmp/sonarqube-${SONAR_VERSION}.zip https://binaries.sonarsource.com/Distribution/sonarqube/sonarqube-${SONAR_VERSION}.zip
yum -y install https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm
yum -y install postgresql14-server postgresql14

echo "[+] Setup postgresql initdb"
/usr/pgsql-14/bin/postgresql-14-setup initdb

echo "[+] Enable postgresql"
systemctl enable --now postgresql-14

echo "[+] Copy postgresql configuration files"
cp /vagrant/config/pg_hba.conf /var/lib/pgsql/14/data/
cp /vagrant/config/postgresql.conf /var/lib/pgsql/14/data/

echo "[+] Restart postgresql"
systemctl restart postgresql-14



# firewall is disabled
#firewall-cmd --permanent --add-port=5432/tcp
#firewall-cmd --reload

echo "[+] Create sonar database and user in postgresql"
sudo -u postgres psql <<_EOF_
CREATE DATABASE sonar;
CREATE USER sonar WITH ENCRYPTED PASSWORD 'secretsql';
GRANT ALL PRIVILEGES ON DATABASE sonar TO sonar;
ALTER DATABASE sonar OWNER TO sonar;
quit
_EOF_

echo "[+] Install SonarQube v9"
cd /tmp
unzip sonarqube-*.zip
mv /tmp/sonarqube-${SONAR_VERSION}/ /opt/sonarqube
rm  -rf /tmp/sonarqube*

echo "[+] Configure SonarQube"
cp /vagrant/config/sonar.properties /opt/sonarqube/conf/

echo "[+] Set SonarQube permissions"
chown -R sonar:sonar /opt/sonarqube

echo "[+] install SonarQube systemd script"
cp /vagrant/config/sonarqube.service /etc/systemd/system/sonarqube.service

echo "[+] Reload systemd daemon"
systemctl daemon-reload

echo "[+] Start SonarQube"
systemctl start sonarqube.service

echo "[+] Enable SonarQube for persistent startup"
systemctl enable sonarqube.service

echo "Finished setup.sh OK for provisioning this VCC SonarQube node"
echo

# put this anywhere you need to stop during troubleshooting this build script
#echo "[+] Premature exit to facilitate troubleshooting"
#exit 0
