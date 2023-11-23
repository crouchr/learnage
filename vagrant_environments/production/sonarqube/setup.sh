#!/usr/bin/env bash
# Bring up the SonarQube - intent is bring up a pet based on this script
# This script assumes a CentOS host
# Files on the Host can be accessed via the /vagrant share

set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning SonarQube node"

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
adduser sonar
echo "[+] Set sonar user password"
echo sonar:myson65-ssword | chpasswd

# install Java
wget -q -O /tmp/jdk-17_linux-x64_bin.rpm https://download.oracle.com/java/17/latest/jdk-17_linux-x64_bin.rpm
yum -y install /tmp/jdk-17_linux-x64_bin.rpm
# Java smoke check
java -version

# Configure node
cp /vagrant/config/motd /etc/

echo "[+] Download SonarQube v9.9.1"
wget -q -O /tmp/sonarqube-9.9.1.69595.zip https://binaries.sonarsource.com/Distribution/sonarqube/sonarqube-9.9.1.69595.zip

yum -y install https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm
yum -y install postgresql14-server postgresql14

echo "[+] Setup postgresql initdb"
/usr/pgsql-14/bin/postgresql-14-setup initdb

echo "[+] Enable postgresql"
systemctl enable --now postgresql-14

echo "[+] Copy postgresql configuration file"
cp /vagrant/config/pg_hba.conf /var/lib/pgsql/14/data/

echo "[+] Restart postgresql"
systemctl restart postgresql-14

echo "[+] Temporarily sudo into postgresql user and create databases"
#chmod 777 /home/vagrant
#sudo -u postgres createuser vagrant -s && sudo -u postgres createdb vagrant && sudo -u postgres createdb sonarqube
#sudo -u postgres createuser sonar -s && sudo -u postgres createdb sonarqube

echo "[+] Change postgresql user password and create SonarQube database"
sudo -u postgres psql <<_EOF_
alter user postgres with password 'secretsql';
quit
_EOF_

echo "[+] Create sonarqube user in postgresql"
sudo -u postgres psql <<_EOF_
CREATE USER sonarqube WITH PASSWORD 'secretsql';
GRANT ALL PRIVILEGES ON DATABASE sonar to sonar;
quit
_EOF_

echo "[+] Install SonarQube"
cd /tmp
unzip sonarqube-*.zip

#echo "[+] Premature exit to facilitate troubleshooting"
#exit 0

mv /tmp/sonarqube-9.9.1.69595/ /opt/sonarqube
rm  -rf /tmp/sonarqube*

echo "[+] install SonarQube systemd script"
cp /vagrant/config/sonarqube.service /etc/systemd/system/sonarqube.service

echo "[+] Reload systemd daemon"
systemctl daemon-reload

echo "[+] Start SonarQube"
systemctl start sonarqube.service

echo "[+] Enable SonarQube for persistent startup"
systemctl enable sonarqube.service
# getting stuck here
#Authentication is required to reload the systemd state.
#Multiple identities can be used for authentication:
# 1.  vagrant
# 2.  crouchr
# 3.  jenkins
#Choose identity to authenticate as (1-3): Failed to execute operation: Connection timed out

#echo "[+] Smoke check SonarQube is running"
#systemctl status sonarqube.service

echo "Finished setup.sh OK for provisioning this SonarQube node"
echo

# put this anywhere you need to stop during troubleshooting this build script
#echo "[+] Premature exit to facilitate troubleshooting"
#exit 0
