# RUN = commands run inside the container
FROM alpine:3.7
#FROM alpine:3.5 - original version - works
LABEL author="Various"
LABEL description="Glastopf honeypot"

# Include dist_files on host - /root gets removed at the end of this script
ADD dist_files/ /root/dist_files/

# Install packages
# RCH : added 'file' & 'joe' packages
# RCH : added re2c to make warning disappear
RUN apk -U --no-cache add \
               file \
               joe \
               autoconf \
               bind-tools \
               build-base \
               git \
               libffi \
               libffi-dev \
               libcap \
               libxslt-dev \
               make \
               php7 \
               php7-dev \
               re2c \
               openssl-dev \
               py-mysqldb \
               py-openssl \
               py-pip \
               py-setuptools \
               python \
               python-dev && \
    pip install --no-cache-dir --upgrade pip && \
# Install php sandbox from git
    git clone --depth=1 https://github.com/mushorg/BFR /opt/BFR && \
    cd /opt/BFR && \
    phpize7 && \
    ./configure \
      --with-php-config=/usr/bin/php-config7 \
      --enable-bfr && \
    make && \
    make install && \
    cd / && \
    rm -rf /opt/BFR /tmp/* /var/tmp/* && \
    echo "zend_extension = "$(find /usr -name bfr.so) >> /etc/php7/php.ini && \
# Install glastopf from git
    git clone --depth=1 https://github.com/mushorg/glastopf.git /opt/glastopf && \
    cd /opt/glastopf && \
    cp /root/dist_files/requirements.txt . && \
    pip install --no-cache-dir . && \
    cd / && \
    rm -rf /opt/glastopf /tmp/* /var/tmp/* && \
    setcap cap_net_bind_service=+ep /usr/bin/python2.7 && \
# Setup user, groups and configs
# rch added : mkdir -p /tmp/glastopf/data && \
    addgroup -g 2000 glastopf && \
    adduser -S -H -u 2000 -D -g 2000 glastopf && \
    mkdir -p /etc/glastopf && \
    mkdir -p /tmp/glastopf/data && \
    mv /root/dist_files/glastopf.cfg /etc/glastopf/ && \
# Clean up
    apk del --purge autoconf \
                    build-base \
                    file \
                    git \
                    libffi-dev \
                    php7-dev \
                    python-dev \
                    py-pip && \
    rm -rf /root/* && \
    rm -rf /var/cache/apk/*

EXPOSE 80

# Set workdir and start glastopf
STOPSIGNAL SIGINT

#USER glastopf:glastopf
USER root:root

WORKDIR /tmp/glastopf/

# /usr/bin/glastopf-runner
CMD cp /etc/glastopf/glastopf.cfg /tmp/glastopf && exec glastopf-runner
