#!/usr/bin/env bash
# Upload the Box file to Vagrant
# This needs testing
vagrant cloud publish -d "RCH CentOS7 Box" --force crouchr/rch-centos-7 1.0.0 virtualbox boxes/rch-centos-7.box
