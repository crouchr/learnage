# ref : https://pypi.org/project/vagrant-metadata/
#python2 -m /home/crouchr/.local/lib/python2.7/site-packages/vagrant_metadata.py \
vagrant-metadata \
--name="crouchr/rch-micro-centos7" \
--description="CentOS 7 Ubuntu 64-bit micro image" \
--baseurl="http://web.ermin/boxes"

scp metadata.json crouchr@web.ermin:/var/www/html/boxes/metadata.json
