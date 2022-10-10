CREATE USER 'mytestuser' IDENTIFIED BY 'password123';

GRANT SELECT, SHOW VIEW ON defaultdb.* TO 'mytestuser';