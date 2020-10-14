# Apache-based reverse proxy
# The Vagrant setup.sh file in this directory is the master in terms of actions required

#FROM centos:7.8.2003
FROM registry:5000/gold-centos7:1.0.0
LABEL author="Richard Crouch"
LABEL description="Apache-based Reverse Proxy"

# Update everything
RUN yum update -y

RUN yum install -y \
httpd httpd-devel mod_ssl

# Generate SSH keys for use by SSHD
#RUN /usr/bin/ssh-keygen -A

# Apache self-signed certificate locations
RUN cd /etc/ssl
RUN mkdir /etc/ssl/private
RUN chmod 700 /etc/ssl/private
RUN echo "192.168.1.15 erminserver.ermin erminserver" >> /etc/hosts

# Apache configuration
COPY apache/index.html /var/www/html/index.html
RUN chown apache:apache /var/www/html/index.html
RUN chmod 755 /var/www/html/index.html
COPY apache/httpd.conf /etc/httpd/conf/
COPY apache/proxy.conf /etc/httpd/conf.d/
COPY apache/ssl.conf /etc/httpd/conf.d/
COPY certs/*.crt /etc/ssl/certs
COPY certs/*.key /etc/ssl/private

# Apache will be run up when container runs
RUN systemctl enable httpd.service

EXPOSE 22
EXPOSE 80
EXPOSE 443

CMD ["/usr/sbin/sshd", "-D"]
