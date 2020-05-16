#!/usr/bin/env bash
# https://documentation.wazuh.com/3.12/installation-guide/installing-wazuh-agent/linux/centos6-or-greater/wazuh_agent_package_centos6_or_greater.html#wazuh-agent-package-centos6-or-greater
# there is a VM with the wazuh server on it - I have downloaded it but no more

sudo rpm --import http://packages.wazuh.com/key/GPG-KEY-WAZUH

sudo cat > /etc/yum.repos.d/wazuh.repo <<\EOF
[wazuh_repo]
gpgcheck=1
gpgkey=https://packages.wazuh.com/key/GPG-KEY-WAZUH
enabled=1
name=Wazuh repository
baseurl=https://packages.wazuh.com/3.x/yum/
protect=1
EOF

WAZUH_MANAGER="192.168.1.99"
sudo yum i-y nstall wazuh-agent

# Optional) Disable the Wazuh repository:
sudo sed -i "s/^enabled=1/enabled=0/" /etc/yum.repos.d/wazuh.repo
