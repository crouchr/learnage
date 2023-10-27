mars-ossec server
-----------------
This is the OSSEC server used for receiving mars honeypot logs
Main objective is to work on the blackrain-specific rules etc and to use this to 
optimise various log formats for easy parsing by OSSEC

This Vagrant machine will be used to create a pet via OVA export as the installation is not easily 
able to be automated in this version.

For the blackrain-ossec version, that will need to be an automated installation if possible

In the end I could only get 2.8.3 working with the mars 2.8.3 agent

<logall>yes</logall> works on 2.8.3 which is the critical functionality