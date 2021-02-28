#
# MXWeather Dockerfile
#
# see https://github.com/Optoisolated/MXWeather
#
# Note: in order to prevent docker from turning Cumulus.ini into a folder, you need to touch it first
# eg. touch /opt/MXWeather/Cumulus.ini
# To build:  docker build -t ubuntu:MXWeather .
# To run:    docker run --name=MXWeather -p 8998:8998 -p 8080:80 -v /opt/MXWeather/data:/opt/CumulusMX/data -v /opt/MXWeather/backup:/opt/CumulusMX/backup -v /opt/MXWeather/log:/var/log/nginx -v /opt/MXWeather/Cumulus.ini:/opt/CumulusMX/Cumulus.ini --device=/dev/hidraw0 -d ubuntu:MXWeather
# Weather data, logs, and settings are persistent outside of the container

# Pull base image.
FROM ubuntu:focal
LABEL Maintainer="MetMiniWX"

# Config Info
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/London
SHELL ["/bin/bash", "-c"]

# Install Nginx.
RUN \
  apt-get update && \
  apt-get install -y software-properties-common && \
  add-apt-repository -y ppa:nginx/stable && \
  apt-get update && \
  apt-get install -y nginx && \
  rm -rf /var/lib/apt/lists/* && \
  echo "\ndaemon off;" >> /etc/nginx/nginx.conf && \
  chown -R www-data:www-data /var/lib/nginx

# Install Packages
RUN apt-get update && \
    apt-get install -y curl tzdata joe ncdu unzip libudev-dev git python3-virtualenv

# Install Mono
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF
RUN echo "deb http://download.mono-project.com/repo/ubuntu bionic/snapshots/5.20.1 main" > /etc/apt/sources.list.d/mono-xamarin.list && \
    apt-get update && \
    apt-get install -y mono-devel ca-certificates-mono fsharp mono-vbnc nuget && \
    rm -rf /var/lib/apt/lists/*
  
# Configure TZData
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# https://github.com/cumulusmx/CumulusMX/releases to get filename and release info
# *** start of my customisation ***
RUN curl -L https://github.com/cumulusmx/CumulusMX/releases/download/b3116/CumulusMXDist3116.zip --output /tmp/CumulusMX.zip
# *** end of my customisation ***

RUN mkdir /opt/CumulusMX && \
  unzip /tmp/CumulusMX.zip -d /opt && \
  chmod +x /opt/CumulusMX/CumulusMX.exe

# Copy the Web Service Files into the Published Web Folder
RUN cp -r /opt/CumulusMX/webfiles/* /opt/CumulusMX/web/

# Define mountable directories.
VOLUME ["/opt/CumulusMX/data","/opt/CumulusMX/backup","/opt/CumulusMX/Reports","/var/log/nginx"]

# Add Start Script# Test File
COPY ./MXWeather.sh /opt/CumulusMX/

# Add Nginx Config
COPY ./nginx.conf /etc/nginx/
COPY ./MXWeather.conf /etc/nginx/sites-available/
RUN ln -s /etc/nginx/sites-available/MXWeather.conf /etc/nginx/sites-enabled/MXWeather.conf && \
  rm /etc/nginx/sites-enabled/default

# Redirect realtime.txt which for some reason is produced in the root folder
RUN touch /opt/CumulusMX/realtime.txt && \
  ln -s /opt/CumulusMX/realtime.txt /opt/CumulusMX/web/realtime.txt

WORKDIR /opt/CumulusMX/
RUN chmod +x /opt/CumulusMX/MXWeather.sh

CMD ["./MXWeather.sh"]

# How to bail
#STOPSIGNAL SIGTERM

# Expose ports.
EXPOSE 80
EXPOSE 8998
