#!/usr/bin/env bash
set -e	# bomb out if any problem

# Running with no run list will register the node to Chef
sudo chef-client --chef-license accept
