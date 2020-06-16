# Basic container for testng networking
FROM alpine:3.11

# Install packages
RUN apk -U --no-cache add \
                      bash \
                      tcpdump \
                      nmap

RUN \
    rm -rf /root/* && \
    rm -rf /var/cache/apk/*

WORKDIR /home
