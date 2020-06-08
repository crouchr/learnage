# RUN = commands run inside the container
# FROM alpine:3.5 - works
FROM alpine:3.7
LABEL author="Various"
LABEL description="Amun honeypot"

# Include dist_files on host - /root gets removed at the end of this script
ADD dist_files/ /root/dist_files/

WORKDIR /opt/amun/

# Install packages
# RCH added joe
RUN apk -U --no-cache add \
               git \
               joe \
               py-pip \
               py-setuptools \
               python \
               python-dev

RUN pip install --no-cache-dir --upgrade pip

# Install Amun from git
RUN git clone --depth=1 https://github.com/zeroq/amun /opt/amun

RUN cp /root/dist_files/amun.conf /opt/amun/conf/amun.conf

# There are more - see mars
EXPOSE 135 139 445 62001 62002 62003

STOPSIGNAL SIGINT

USER root:root

# Give a shell prompt while debugging
#CMD exec ash
CMD ./amun_server.py
