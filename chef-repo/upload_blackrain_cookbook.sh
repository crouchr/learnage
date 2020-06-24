#!/usr/bin/env bash
# Script to upload cookbooks to the Managed Chef Server

sudo knife cookbook upload \
blackrain \
-s https://manage.chef.io/organizations/blackrainermin --cookbook-path cookbooks
