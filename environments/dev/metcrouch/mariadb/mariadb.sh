# scipt to creat the metmini database
create database metminidb;
create user 'metmini'@localhost identified by 'metmini';
grant all on metmini.* to 'metmini' identified by 'metmini';
exit
