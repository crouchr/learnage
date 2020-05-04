# Install Spacewalk 2.9
# reference https://www.itzgeek.com/how-tos/linux/centos-how-tos/how-to-install-spacewalk-on-centos-7-rhel-7.html

cp /vagrant/answerfile.txt /home/vagrant/answerfile.txt

sudo yum install -y yum-plugin-tmprepo
sudo yum install -y spacewalk-repo --tmprepo=https://copr-be.cloud.fedoraproject.org/results/%40spacewalkproject/spacewalk-2.9/epel-7-x86_64/repodata/repomd.xml --nogpg
sudo yum -y install spacewalk-setup-postgresql
sudo yum -y install spacewalk-postgresql
sudo yum -y install spacewalk-utils

sudo spacewalk-setup --answer-file answerfile.txt

echo "Spacewalk installation complete"
echo "Now visit https://spacewalk.ermin to create the Spacewalk administrator account."
