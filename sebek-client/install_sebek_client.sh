# Install your keys first
WAFFLE='-i /home/crouchr/.ssh/rch-nvm-sshkey crouchr@192.168.1.111'
WAFFLE_SUDO='-i /home/crouchr/.ssh/rch-nvm-sshkey crouchr@192.168.1.111 sudo sh -c '

ssh ${WAFFLE} 'uname -a'
ssh ${WAFFLE} 'ps'
ssh ${WAFFLE} 'ls -laF'

echo "Modify /etc/hosts ..."
ssh ${WAFFLE_SUDO} "'echo 192.168.1.102 web.ermin.lan >> /etc/hosts'"

echo "Configure Linux source ..."
ssh ${WAFFLE_SUDO} "'ln -s /usr/src/linux-2.4.33.3 /usr/src/linux-2.4'"

echo "Clear out /tmp ..."
ssh ${WAFFLE_SUDO} "'cd /tmp && rm -rf *'"

echo "Build sebek client ..."
ssh ${WAFFLE_SUDO} "'curl -o /tmp/sebek-linux-3.0.3.tar.gz http://web.ermin.lan/br2020-packages/sebek-linux-3.0.3.tar.gz'"
ssh ${WAFFLE_SUDO} "'cd /tmp && gunzip sebek-linux-3.0.3.tar.gz'"
ssh ${WAFFLE_SUDO} "'cd /tmp && tar xvf sebek-linux-3.0.3.tar'"
ssh ${WAFFLE_SUDO} "'cd /tmp/sebek-linux-3.0.3 && ./configure && make'"

#ssh ${WAFFLE} 'cd /home'
#ssh ${WAFFLE} 'pwd'

