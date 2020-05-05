#!/usr/bin/env bash
# Script to upload cookbooks to the Managed Chef Server

sudo knife cookbook upload \
logrotate \
-s https://manage.chef.io/organizations/blackrainermin --cookbook-path cookbooks

sudo knife cookbook upload \
cron \
-s https://manage.chef.io/organizations/blackrainermin --cookbook-path cookbooks

sudo knife cookbook upload \
ntp \
-s https://manage.chef.io/organizations/blackrainermin --cookbook-path cookbooks

sudo knife cookbook upload \
chef-client \
-s https://manage.chef.io/organizations/blackrainermin --cookbook-path cookbooks
