#!/usr/bin/env bash
# Script to upload cookbooks to my Chef Server

sudo knife cookbook upload \
logrotate \
-s https://chef.ermin.com/organizations/br2023 --cookbook-path ../cookbooks

sudo knife cookbook upload \
cron \
-s https://chef.ermin.com/organizations/br2023 --cookbook-path ../cookbooks

sudo knife cookbook upload \
ntp \
-s https://chef.ermin.com/organizations/br2023 --cookbook-path ../cookbooks

sudo knife cookbook upload \
chef-client \
-s https://chef.ermin.com/organizations/br2023 --cookbook-path ../cookbooks
