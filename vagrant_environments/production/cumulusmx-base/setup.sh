#!/usr/bin/env bash
# Bring up the CumulusMX box
# see https://github.com/Optoisolated/MXWeather
# This script is not idempotent - you have to destroy the VBOX each time

set -e	    # bomb out if any problem

echo
echo "Started setup.sh for provisioning CumulusMX node"

# ==========================================================================================================
# https://github.com/cumulusmx/CumulusMX/releases to get filename and release info
export CUMULUSMX_CODE='https://github.com/cumulusmx/CumulusMX/releases/download/b3116/CumulusMXDist3116.zip'
# ==========================================================================================================

export TZ=Europe/London

# Install Nginx.
apt-get update
apt-get install -y software-properties-common
add-apt-repository -y ppa:nginx/stable
apt-get update
apt-get install -y nginx
rm -rf /var/lib/apt/lists/*
echo "\ndaemon off;" >> /etc/nginx/nginx.conf
chown -R www-data:www-data /var/lib/nginx

# Install Packages
apt-get update
apt-get install -y curl tzdata joe ncdu unzip libudev-dev git python3-virtualenv

# Install Mono
apt-get update
apt-get install -y curl
rm -rf /var/lib/apt/lists/*

apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF
echo "deb http://download.mono-project.com/repo/ubuntu bionic/snapshots/5.20.1 main" > /etc/apt/sources.list.d/mono-xamarin.list
apt-get update
apt-get install -y mono-devel ca-certificates-mono fsharp mono-vbnc nuget
rm -rf /var/lib/apt/lists/*

# Configure TZData
ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# do this or /var/log/syslog gets filled with rubbish
cp /vagrant/multipath.conf /etc/multipath.conf


# N.B. at this point, the box is ready to have CumulusMX installed

# Install CumulusMX
curl -L ${CUMULUSMX_CODE} --output /tmp/CumulusMX.zip

mkdir -p /opt/CumulusMX
unzip /tmp/CumulusMX.zip -d /opt
chmod +x /opt/CumulusMX/CumulusMX.exe

# Copy the Web Service Files into the Published Web Folder
cp -r /opt/CumulusMX/webfiles/* /opt/CumulusMX/web/

# Add Start Script# Test File
cp /vagrant/MXWeather.sh /opt/CumulusMX/

# Add Nginx Config
cp /vagrant/nginx.conf /etc/nginx/
cp /vagrant/MXWeather.conf /etc/nginx/sites-available/
ln -s /etc/nginx/sites-available/MXWeather.conf /etc/nginx/sites-enabled/MXWeather.conf
rm /etc/nginx/sites-enabled/default

# Redirect realtime.txt which for some reason is produced in the root folder
touch /opt/CumulusMX/realtime.txt
ln -s /opt/CumulusMX/realtime.txt /opt/CumulusMX/web/realtime.txt

#WORKDIR /opt/CumulusMX/
chmod +x /opt/CumulusMX/MXWeather.sh

# run using
# vagrant@cumulusmx:/opt/CumulusMX$ sudo ./MXWeather.sh &

echo "Finished setup.sh for provisioning CumulusMX node"
