# RUN = commands run inside the container
# Needs to have dev tools removed once perl module built
# FROM alpine:3.5 - works
# https://serverfault.com/questions/364452/silent-and-scripted-install-of-cpan-and-perl-modules
# perl -MCPAN -e 'install Your::Package'

FROM alpine:3.9
LABEL author="Various"
LABEL description="Netflow honeypot"

# answer yes to all Perl install questions
ENV PERL_MM_USE_DEFAULT=1

# Include dist_files on host - /root gets removed at the end of this script
ADD dist_files/ /root/dist_files/
RUN mkdir -p /opt/netflow

WORKDIR /opt/netflow

RUN apk -U --no-cache add \
               perl \
               build-base \
               joe \
               tcpdump \
               nmap

#RUN cp /root/dist_files/Net-Flow-0.04.tar.gz /opt/netflow/Net-Flow-0.04.tar.gz
RUN cp /root/dist_files/Net-Flow-1.003.tar.gz /opt/netflow/Net-Flow-1.003.tar.gz
RUN cp /root/dist_files/blackrain_netflow.pl /opt/netflow/blackrain_netflow.pl

WORKDIR /opt/netflow
#RUN gunzip Net-Flow-0.04.tar.gz
#RUN tar xvf Net-Flow-0.04.tar
RUN gunzip Net-Flow-1.003.tar.gz
RUN tar xvf Net-Flow-1.003.tar

#WORKDIR /opt/netflow/Net-Flow-0.04
WORKDIR /opt/netflow/Net-Flow-1.003
RUN perl Makefile.PL
RUN make
RUN make test
RUN make install

STOPSIGNAL SIGINT

USER root:root
