#!/bin/bash -eux

sed -i 's/^\(Defaults\s\+requiretty\)/#\1/' /etc/sudoers
