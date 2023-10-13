#!/usr/bin/env bash
# Script to upload cookbooks to my Chef Server

sudo knife cookbook upload \
blackrain \
-s https://chef.ermin.com/organizations/br2023 --cookbook-path cookbooks
#-s https://manage.chef.io/organizations/blackrainermin --cookbook-path cookbooks