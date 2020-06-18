# RUN = commands run inside the container
# Needs to have dev tools removed once perl module built
# https://serverfault.com/questions/364452/silent-and-scripted-install-of-cpan-and-perl-modules
# perl -MCPAN -e 'install Your::Package'
# Net-Flow-0.004 was the original version on Blackrain
# Found Net-Flow source at : http://admin03.joeswebhosting.net/CPAN/authors/id/A/AC/ACFEREN/
# Samplicator latest source at : https://mirrors.sohu.com/gentoo/distfiles/e7/
# https://perlmaven.com/how-to-build-perl-from-source-code

# FROM alpine:3.10 - works
FROM alpine:3.11

LABEL author="Richard Crouch"
LABEL description="Netflow"

# answer yes to all Perl install questions
ENV PERL_MM_USE_DEFAULT=1

# Include dist_files on host - /root gets removed at the end of this script
ADD dist_files /root/dist_files/
RUN mkdir -p /opt/netflow

WORKDIR /opt/netflow

RUN apk -U --no-cache add \
               perl \
               build-base \
               libpcap-dev \
               joe \
               tcpdump \
               nmap

#RUN cp /root/dist_files/Net-Flow-0.04.tar.gz /opt/netflow/Net-Flow-0.04.tar.gz
RUN cp /root/dist_files/Net-Flow-1.003.tar.gz /opt/netflow/Net-Flow-1.003.tar.gz
RUN cp /root/dist_files/blackrain_netflow.pl /opt/netflow/blackrain_netflow.pl
RUN cp /root/dist_files/samplicator-1.3.8rc1.tar.gz /opt/netflow/samplicator-1.3.8rc1.tar.gz
RUN cp /root/dist_files/fprobe_1.1.orig.tar.gz /opt/netflow/fprobe_1.1.orig.tar.gz

WORKDIR /opt/netflow
RUN gunzip Net-Flow-1.003.tar.gz
RUN tar xvf Net-Flow-1.003.tar

RUN gunzip samplicator-1.3.8rc1.tar.gz
RUN tar xvf samplicator-1.3.8rc1.tar

RUN gunzip fprobe_1.1.orig.tar.gz
RUN tar xvf fprobe_1.1.orig.tar

# Build and install Net-Flow module
WORKDIR /opt/netflow/Net-Flow-1.003
RUN perl Makefile.PL
RUN make
RUN make test
RUN make install

# Build and install Samplicator
WORKDIR /opt/netflow/samplicator-1.3.8rc1
RUN ./configure
RUN make
RUN make install

# Build and install fprobe
WORKDIR /opt/netflow/fprobe-1.1
RUN ./configure
RUN make
RUN make install

STOPSIGNAL SIGINT

USER root:root
