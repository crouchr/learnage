#!/bin/bash
# script to create the metmini database and add tables

mysql -u root <<MYSQL_SCRIPT
CREATE DATABASE metminidb;
CREATE USER 'metmini'@localhost identified by 'metmini';
GRANT ALL ON metmini.* to 'metmini' identified by 'metmini';
FLUSH PRIVILEGES;
MYSQL_SCRIPT

mysql -u root <<MYSQL_SCRIPT
CREATE USER 'metmini'@erminserver.localdomain identified by 'metmini';
CREATE DATABASE metminidb;
GRANT ALL ON metminidb.* to 'metmini' identified by 'metmini';
FLUSH PRIVILEGES;
SHOW GRANTS FOR 'metmini'@erminserver.localdomain;
MYSQL_SCRIPT

mysql -u root <<MYSQL_SCRIPT
USE metminidb;
DROP TABLE metminilogs;
CREATE TABLE metminilogs
(
id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
ts_local DATETIME NOT NULL,
ts_utc DATETIME NOT NULL,
julian INT NOT NULL,
pressure INT NOT NULL,
ptrend VARCHAR(10) NOT NULL,
wind_quadrant VARCHAR(10) NOT NULL,
wind_strength VARCHAR(10) NOT NULL,
forecast VARCHAR(128) NOT NULL,
bforecast VARCHAR(32) NOT NULL,
oforecast VARCHAR(32) NOT NULL,
coverage VARCHAR(16) NOT NULL,
location VARCHAR(64) NOT NULL,
yest_rain int NOT NULL,
yest_wind VARCHAR(10) NOT NULL,
yest_min_temp INT NOT NULL,
yest_max_temp INT NOT NULL,
data_type VARCHAR(16) NOT NULL
);
MYSQL_SCRIPT

mysql -u root <<MYSQL_SCRIPT
USE metminidb;
DROP TABLE actual;
CREATE TABLE actual
(
id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
ts_local DATETIME NOT NULL,
ts_utc DATETIME NOT NULL,
julian INT NOT NULL,
hour_utc INT NOT NULL,
location VARCHAR(64) NOT NULL,
main VARCHAR(32) NOT NULL,
description VARCHAR(32) NOT NULL,
pressure INT NOT NULL,
wind_speed FLOAT NOT NULL,
wind_deg INT NOT NULL,
wind_quadrant VARCHAR(8) NOT NULL,
wind_strength INT NOT NULL,
wind_gust FLOAT NOT NULL,
temp FLOAT NOT NULL,
feels_like FLOAT NOT NULL,
dew_point FLOAT NOT NULL,
uvi FLOAT NOT NULL,
humidity INT NOT NULL,
visibility INT NOT NULL,
rain FLOAT NOT NULL,
snow FLOAT NOT NULL,
coverage INT NOT NULL,
source VARCHAR(32) NOT NULL,
lat VARCHAR(8) NOT NULL,
lon VARCHAR(8) NOT NULL,
tz VARCHAR(32) NOT NULL,
tz_offset INT NOT NULL,
ts_epoch INT NOT NULL,
sunrise_local TIMESTAMP NOT NULL,
sunset_local TIMESTAMP NOT NULL
);
MYSQL_SCRIPT

mysql -u root <<MYSQL_SCRIPT
USE metminidb;
DROP TABLE forecasts;
CREATE TABLE forecasts
(
id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
ts_local DATETIME NOT NULL,
ts_utc DATETIME NOT NULL,
julian INT NOT NULL,
location VARCHAR(64) NOT NULL,
pressure INT NOT NULL,
ptrend VARCHAR(10) NOT NULL,
wind_quadrant VARCHAR(8) NOT NULL,
wind_strength INT NOT NULL,
slope FLOAT NOT NULL,
source VARCHAR(32) NOT NULL,
forecast VARCHAR(128) NOT NULL
);
MYSQL_SCRIPT
