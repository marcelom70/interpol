CREATE DATABASE interpol_london;
CREATE USER interpol_user WITH PASSWORD 'Interpol@123';
ALTER ROLE interpol_user SET client_encoding TO 'utf8';
GRANT ALL PRIVILEGES ON DATABASE interpol_london TO interpol_user;