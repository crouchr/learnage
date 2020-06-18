# Basic container for testing networking
FROM alpine:3.11

LABEL author="Various"
LABEL description="Debugging container"

# Install packages
RUN apk -U --no-cache add \
                      bash \
                      tcpdump \
                      tcpflow \
                      nmap

RUN \
    rm -rf /root/* && \
    rm -rf /var/cache/apk/*

WORKDIR /home
