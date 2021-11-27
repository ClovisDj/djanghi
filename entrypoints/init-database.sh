#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER docker;
    CREATE DATABASE djanghi-db;
    GRANT ALL PRIVILEGES ON DATABASE djanghi-db TO docker;
    CREATE DATABASE djanghi-test-db;
    GRANT ALL PRIVILEGES ON DATABASE djanghi-test-db TO docker;
EOSQL