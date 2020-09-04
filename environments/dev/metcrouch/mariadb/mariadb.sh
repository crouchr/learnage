#!/bin/bash
# script to create the metmini database

#mysql -u root <<MYSQL_SCRIPT
#CREATE DATABASE metminidb;
#CREATE USER 'metmini'@localhost identified by 'metmini';
#GRANT ALL ON metmini.* to 'metmini' identified by 'metmini';
#FLUSH PRIVILEGES;
#MYSQL_SCRIPT

CREATE USER 'metmini'@erminserver.localdomain identified by 'metmini';
CREATE DATABASE metminidb;
GRANT ALL ON metminidb.* to 'metmini' identified by 'metmini';
FLUSH PRIVILEGES;
SHOW GRANTS FOR 'metmini'@erminserver.localdomain;

USE metminidb;

DROP TABLE metminilogs;
CREATE TABLE metminilogs
(
  date DATE NOT NULL,
  time TIME NOT NULL,
  data_type VARCHAR(10) NOT NULL,
  pressure INT NOT NULL,
  ptrend VARCHAR(10) NOT NULL,
  wind_dir VARCHAR(10) NOT NULL,
  wind_strength VARCHAR(10) NOT NULL,
  bresser_forecast VARCHAR(10) NOT NULL,
  oregon_forecast VARCHAR(10),
  clouds VARCHAR(32),
  location VARCHAR(32) NOT NULL,
  notes VARCHAR(32),
  yest_rain INT,
  yest_wind_strength INT,
  yest_min_temp INT,
  yest_max_temp INT,
  yest_notes VARCHAR(32)
);

DESCRIBE metminilogs;

mysql -u root <<MYSQL_SCRIPT
CREATE TABLE METMINI (
pressure
);
MYSQL_SCRIPT
