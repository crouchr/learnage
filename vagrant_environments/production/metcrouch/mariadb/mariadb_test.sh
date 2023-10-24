#!/bin/bash
# script to create the metmini database

mysql -u root <<MYSQL_SCRIPT
CREATE DATABASE metminidb;
CREATE USER 'metmini'@erminserver.localdomain identified by 'metmini';
GRANT ALL ON metmini.* to 'metmini' identified by 'metmini';
FLUSH PRIVILEGES;
MYSQL_SCRIPT



