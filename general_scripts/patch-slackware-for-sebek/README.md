plan
K2.6.16 was used to successfully build sebek 2.6 module
So try to build a Slackware 13.0 VM and use K2.6.16 kernel - compiled from source


Instructions - do as root
https://docs.slackware.com/howtos:slackware_admin:kernelbuilding
download linux source (bz2) to /home/crouchr
cd home/crouchr
wget http://192.168.1.102/br2020-packages/linux-2.6.16.tar.bz2
wget http://192.168.1.102/br2020-packages/config-generic-smp-2.6.24.5-smp
cp config-generic-smp-2.6.24.5-smp /usr/src/linux/.config

tar -C /usr/src -jxvf linux-2.6.16.tar.bz2
cd /usr/src
rm linux 
ln -s linux-2.6.16 linux

cd /usr/src/linux
SNAPSHOT
make oldconfig

just hit RETURN key and accept defaults x 40
<snapshot>
make menuconfig
<snapshot>  -br2020 is label
make bzImage modules













Notes

