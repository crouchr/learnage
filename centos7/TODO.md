TODO
====

ALL BOXES
=========
- Remove the other rch folders etc
- Cut out all the variables
- Look at steve's clean up scripts - zeroing out to save space etc.
- Add the crouchr user using scripts (and check can login) - using key and normal password
- Add inspec test to check that httpd / apache has been installed
- Use the box file in my learningchef setup to check authentication
- Do not require sudo in all th scripts to be able to complete the installation
- Add any other useful parameters to the basic Vagrant file, e.g. explicit declaration of num cpus etc.
- Convert to use consistent naming i.e. eth0
- Add a script to list the number of installed packages so can quantify 'improvements'
- The hostname needs to be parameterised on the command-line - its the same on the two centos7 builds - not usre what this does to Spacewalk
- Get Chef registration working

DONE
====
- Add Vbox guest tools
- Create the Vagrant file that can be used to bring the machine up
- Rename folder to hellobox

rch-centos-7
============
- Add hostname script from blackrain
- align ks.cfg - root pw -> vagrant
- add box description and versioning to rch-centos7


micro-centos
============
- Use netinstall centos image as per Steve's recommendations - I have downloaded it - just need to reference it and use new checksum
