#!/usr/bin/env bash
# Bring up the PyPi server - intent is bring up a pet based on this script
# This script assumes a CentOS host
# Files on the Host can be accessed via the /vagrant share

set -e	# bomb out if any problem

echo 
echo "Started setup.sh for provisioning PyPi node"

PYTHON_VERSION=3.9.18

# Configure node
cp /vagrant/config/motd /etc/motd

# Check for patch updates - slows up boot so need a way of avoiding this
yum update -y --disableplugin=fastestmirror

yum install -y wget curl unzip
yum install -y gcc openssl-devel bzip2-devel libffi-devel

# Do this before Python is installed so python installer does not complain
export PATH=${PATH}:/usr/local/bin/
echo "${PATH}"

echo "[+] Install Python ${PYTHON_VERSION}"
curl -O https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz
tar -xzf Python-${PYTHON_VERSION}.tgz
cd Python-${PYTHON_VERSION}/
./configure --enable-optimizations
make altinstall
ln -s /usr/local/bin/python3.9 /usr/bin/python3

echo "[+] Python smoke tests"
# /usr/local/bin/pip3.9 --version
# /usr/local/bin/python3.9 --version
#pip3.9 --version
#python3.9 --version
python3 --version

echo "[+] Install PyPi Server with authentication capabilities"
cp /vagrant/install/requirements.txt /tmp/
pip3.9 install -r /tmp/requirements.txt --root-user-action=ignore --disable-pip-version-check
pip3.9 install --root-user-action=ignore --disable-pip-version-check pypiserver['passlib']==2.0.1

echo "[+] Install some test wheels/packages"
mkdir /home/vagrant/packages
cp /vagrant/packages/*.whl /home/vagrant/packages/

# generate on web-server
echo "[+] Install authentication password file"
cp /vagrant/config/htpasswd.txt /home/vagrant/.htpasswd.txt

echo "[+] Install PyPi systemd script"
cp /vagrant/config/pypi.service /etc/systemd/system/pypi.service
chmod 0755 /etc/systemd/system/pypi.service

echo "[+] Start the PyPi server"
#/usr/local/bin/pypi-server run -p 8080 -a update,download --log-file /var/log/pypiserver.log /home/vagrant/packages &
# run with no authentication
# /usr/local/bin/pypi-server run -p 8080 --log-file /var/log/pypiserver.log /home/vagrant/packages &
/usr/local/bin/pypi-server run -p 8080 --log-file /var/log/pypiserver.log -a update,download --passwords /home/vagrant/.htpasswd.txt --disable-fallback --overwrite /home/vagrant/packages &


# systemctl not working
#echo "[+] Reload systemd daemon"
#systemctl daemon-reload

#echo "[+] Start PyPi Server"
#systemctl start pypi.service

#echo "[+] Enable PyPi for persistent startup"
#systemctl enable pypi.service

echo "Finished setup.sh OK for provisioning this PyPi node"
echo

# put this anywhere you need to stop during troubleshooting this build script
# echo "[+] Premature exit to facilitate troubleshooting"
# exit 0