README.md
=========
Blackrain (Slackware '15' version) build notes



Packages built from source/3rd party pre-built packages
-------------------------------------------------------
The following were built from source as they were either not in sbopkg or failed to build in sbopkg
- barnyard2
 get package from  
 wget --no-check-certificate https://slack.conraid.net/repository/slackware64-current/barnyard2/barnyard2-2_1.13-x86_64-9cf.txz

Packages built with sbopkg
--------------------------
- libdnet (dumbnet) 
- daq
- snort


Technical Debt
--------------
- barnyard is not the latest version

References/HOWTOs
-----------------
- How to get a configure file : https://developer.gnome.org/anjuta-build-tutorial/stable/create-autotools.html.en
