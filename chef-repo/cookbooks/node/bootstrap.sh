# Set hostname
echo '>>> entered setup.sh...'

hostnamectl set-hostname testbox.ermin.com

cat >> /etc/hosts <<EOL
# Added during Chef Vagrant run
192.168.1.70  chef chef.ermin.com
192.168.1.5   kube kube.ermin.com
192.168.1.6   j1900 j1900.ermin.com
EOL

echo '<<< exited setup.sh...'
