#!/usr/bin/env bash
# Script to upload cookbooks to my Chef Server

sudo knife cookbook upload \
hpot-centos7 \
-s https://chef.ermin.com/organizations/br2023 --cookbook-path ../cookbooks
