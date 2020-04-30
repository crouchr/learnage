#!/usr/bin/env bash
# reference : https://medium.com/@glmdev/registering-spacewalk-clients-b2f42f9f8759
# is there a hostname I can use to register with - see NVM

ERMIN_SPACEWALK_KEY='1-77eb0ab0977438fc59537a0bbab5e698'    # See Spacewalk UI System / Activation Key

sudo rhnreg_ks \
--serverUrl=https://spacewalk.ermin/XMLRPC \
--force \
--profilename=$(/bin/hostname -f) \
--sslCACert=/usr/share/rhn/RHN-ORG-TRUSTED-SSL-CERT \
--activationkey=${ERMIN_SPACEWALK_KEY}

sudo rhn-profile-sync
sudo systemctl enable osad
sudo systemctl restart osad

# Is this to do with config synch which I may not need
sudo rhn-actions-control --enable-all

# One more for luck
sudo rhn-profile-sync

# Note the use of Channel Label not Channel Name
sudo spacewalk-channel --add -c centos-7 --user crouchr --password S0lab0sch
