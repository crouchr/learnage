# Apache-based reverse proxy
FROM centos:7.8.2003
LABEL author="Richard Crouch"
LABEL description="Apache-based Reverse Proxy"

# Include dist_files on host - /root gets removed at the end of this script
#ADD dist_files /root/dist_files/

#WORKDIR /opt/amun/
# Add the EPEL repo
RUN yum install -y epel-release

# Update everything - only when initial development has been done
RUN yum update -y

RUN yum install -y \
which openssh openssh-server openssh-clients openssl-libs net-tools httpd httpd-devel mod_ssl

# Generate SSH keys for use by SSHD
RUN /usr/bin/ssh-keygen -A

RUN cd /etc/ssl
RUN mkdir /etc/ssl/private
RUN chmod 700 /etc/ssl/private

COPY apache/index.html /var/www/html/index.html
RUN chown apache:apache /var/www/html/index.html
RUN chmod 755 /var/www/html/index.html

COPY apache/httpd.conf /etc/httpd/conf/
COPY apache/proxy.conf /etc/httpd/conf.d/
COPY apache/ssl.conf /etc/httpd/conf.d/

COPY certs/*.crt /etc/ssl/certs
COPY certs/*.key /etc/ssl/private

RUN systemctl enable httpd.service

EXPOSE 22
EXPOSE 80
EXPOSE 443

CMD ["/usr/sbin/sshd", "-D"]
