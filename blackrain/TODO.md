TODO
====
- Get a basic Jenkins build job to run buidit.sh - and then make it on a weekly cron basis
- Add start and end time to buildit.sh so I know how long it took
- Remove the other rch folders etc
- Cut out all the variables
- Add the crouchr user using scripts (and check can login) - using key and normal password
- Add inspec tests
- Do not require sudo in all the scripts to be able to complete the installation - see Michaels solution
- Add any other useful parameters to the basic Vagrant file, e.g. explicit declaration of num cpus etc.
- Final part of build is to uninstall gcc and build tools etc

TO BE TESTED
============
- Set a hostname
- Disable SELINUX in Kickstart file

DONE
====


BUGS
====
- The crouch ssh key is stored in a Mac-specific folder - needs to be OS-independent
- rch-waf is not building - hard disk error
- Install a chef client 
- Uninstall the development tools needed to compile guest additions - gcc, perl, kernel-headers
