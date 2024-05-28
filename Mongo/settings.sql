CREATE TABLESPACE trab_tables DATAFILE 'trab_tables.dbf' SIZE 500M;

ALTER SESSION set "_ORACLE_SCRIPT"=true;

CREATE USER nosql IDENTIFIED BY nosql DEFAULT TABLESPACE trab_tables;
GRANT CONNECT, RESOURCE TO nosql;
GRANT CREATE VIEW TO nosql;

ALTER USER nosql QUOTA UNLIMITED ON trab_tables;

CONNECT nosql/nosql;

SELECT table_name 
FROM user_tables;
